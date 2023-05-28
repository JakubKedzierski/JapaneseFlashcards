import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kafka import  KafkaProducer, KafkaConsumer
from config import KAFKA_SERVER, QUIZ_TOPIC, KAFKA_GENERATE_TOPIC, KAFKA_USER_TOPIC, QUIZ_URL
import asyncio
import uvicorn
import schedule
import json

from database import users, flashcards, quizes, database
from sqlalchemy import select
from datetime import datetime


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

quiz_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

async def send_quiz_job():
    print("[Quiz Service] Quiz time - generating quiz for current month")
    # get users data
    try:
        async with database.transaction():
            query = select(users)
            users_data = await database.fetch_all(query)
    except Exception as e:
        print("[Quiz Service]: db error: {}".format(e))
        return
    
    print("[Quiz service] get users data from db : {} ".format(users_data))
    
    for user in users_data: 
        user_id = user["id"]
        await send_quiz_for_single_user(user_id)

async def send_quiz_for_single_user(user_id):
    quiz_date = datetime.today().replace(day=1).date()

    # get users flashcards data
    async with database.transaction():
        query = select(flashcards).where(flashcards.c.user_id == user_id) #need to collect flashcards fron current month only - add date in flashcard
        users_flashcards_data = await database.fetch_all(query)

    if not users_flashcards_data:
        print("[Quiz Service]: user {} doesn't have any flashcard, continue".format(user_id))
        return

    users_flashcards_data = [dict(row) for row in users_flashcards_data]
    users_flashcards_data_json = json.dumps(users_flashcards_data)
    quiz_content = json.dumps(users_flashcards_data_json)

    # insert quiz
    try:
        async with database.transaction():
            quiz_db = {"user_id":user_id, "date": quiz_date, "quiz_content":quiz_content}
            query = quizes.insert().values(**quiz_db)
            quiz_id = await database.execute(query)
    except Exception as e:
        print("[Quiz Service]: Saving quiz has failed, db error: {}".format(e))

    print("[Quiz Service] Quiz time - sending quiz to other services for user {}".format(user_id))
    
    quiz = {"user_id" : user_id, "quiz_msg" : "Here is your quiz: {}{}".format(QUIZ_URL, quiz_id)}
    quiz_producer.send(QUIZ_TOPIC, json.dumps(quiz).encode("utf-8"))



async def schedule_task():
    print("[Quiz Service] Init schedule task")

    quiz_time = "12:00:00"
    schedule.every().day.at(quiz_time).do(send_quiz_job)
    #schedule.every(30).seconds.do(send_quiz_job)
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

async def ProcessUsers():
    consumer = KafkaConsumer(
        KAFKA_USER_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Quiz service] Start processing users \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]

                    print("[Quiz service] received user: {} ".format(user_id))

                    async with database.transaction():
                        user_db = {"id":user_id}
                        query = users.insert().values(**user_db)
                        await database.execute(query)
                        
                    print("[Quiz service]  user: {} saved to db ".format(user_id))

        await asyncio.sleep(1)


async def ProcessFlashcards():
    consumer = KafkaConsumer(
        KAFKA_GENERATE_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Quiz service] Start processing flashcards \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:

                    # flaschard data
                    user_id = record.value["user_id"]
                    word = record.value["word"]
                    hiragana = record.value["hiragana"]
                    kanji = record.value["kanji"]

                    print("[Quiz service] received flashcard: {} {} {} {} ".format(user_id, word, hiragana, kanji))

                    async with database.transaction():
                        flashcard_db = {"user_id":user_id, "word":word, "hiragana":hiragana, "kanji":kanji}
                        query = flashcards.insert().values(**flashcard_db)
                        await database.execute(query)                  

        await asyncio.sleep(1)

#get quiz for user
@app.get("/quiz/{user_id}", status_code=200)
async def get_quiz_data(user_id: int):
    async with database.transaction():
        # not processing date for now
        #quiz_date = datetime.today().replace(day=1).date()
        #query = select(quizes).where(quizes.c.user_id == user_id, quizes.c.date == quiz_date).order_by(quizes.c.date)
        
        query = select(quizes).where(quizes.c.user_id == user_id).order_by(quizes.c.date)
        x = await database.fetch_one(query)

    return x


@app.post("/debug_endpoints/send_quizes", status_code=200)
async def send_quizes():
    await send_quiz_job()
    return '[Quiz Service]: Quiz sent for all users'

@app.post("/debug_endpoints/send_single_quiz/{id}", status_code=200)
async def send_single_quiz(id: int):
    await send_quiz_for_single_user(id)
    return '[Quiz Service]: Quiz sent for single user'


@app.on_event("startup")
async def startup():
    app.schedule_task = asyncio.create_task(schedule_task())
    app.users_task = asyncio.create_task(ProcessUsers())
    app.flashcard_task = asyncio.create_task(ProcessFlashcards())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003,  reload=True, log_level="info")