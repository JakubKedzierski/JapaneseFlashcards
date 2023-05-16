import json
from fastapi import FastAPI
from kafka import KafkaConsumer
from send_email import send_email_async
import asyncio

from config import KAFKA_SERVER, KAFKA_GENERATE_TOPIC, KAFKA_USER_TOPIC, QUIZ_TOPIC
import asyncio
import requests
from database import users, database
from sqlalchemy import select

app = FastAPI()

async def ProcessUsers():
    consumer = KafkaConsumer(
        KAFKA_USER_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Notification service] Start processing users \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    user_email = record.value["user_email"]
                    user_phone = record.value["user_phone"]

                    print("[Notification service] received user: {} {} {} ".format(user_id, user_email, user_phone))

                    async with database.transaction():
                        user_db = {"id":user_id, "user_email":user_email, "user_phone":user_phone}
                        query = users.insert().values(**user_db)
                        await database.execute(query)

        await asyncio.sleep(1)


async def ProcessFlashcards():
    consumer = KafkaConsumer(
        KAFKA_GENERATE_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Notification service] Start processing flashcards \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:

                    # flaschard data
                    user_id = record.value["user_id"]
                    kanji = record.value["kanji"]
                    hiragana = record.value["hiragana"]
                    word = record.value["word"]

                    # get user data
                    async with database.transaction():
                        query = select(users).where(users.c.id == user_id)
                        user_data = await database.fetch_one(query)

                    user_id = user_data["user_id"]
                    user_email = user_data["user_email"]
                    phone = user_data['user_phone']
                    print("[Notification service] get user data from db : {} {} ".format(user_id, user_email))

                    """
                    # old endpoint idea
                    get_request = "http://localhost:8002/user/{}".format(user_id)
                    response = requests.get(get_request)
                    user_data = []
                    if response.status_code != 200:
                        print("User data request Error")
                        continue
                    else:
                        user_data = response.json()
                    if "user_email" not in user_data or "user_phone" not in user_data:
                        print("Bad user data")
                        continue
                    email = user_data['user_email']
                    phone = user_data['user_phone']
                    print("Notifications: got flashcard user_id: {}, email: {}, phone: {}".format(user_id, email, phone))
                    """

                    # send email
                    text_msg = "Here your flaschard: \nhiragana={}, kanji={}, translation={}".format(hiragana, kanji, word)
                    await send_email_async('Flashcard', user_email, text_msg)

                    # send SMS
                    # if phone present:
                        # send SMS

        await asyncio.sleep(1)


async def ProcessQuizzes():
    consumer = KafkaConsumer(
        QUIZ_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Notification service] Start processing quizzes \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:

                    # quiz data
                    user_id = record.value["user_id"]
                    quiz_msg = record.value["quiz_msg"]

                    print("[Notification service] got quiz  {} {}".format(user_id, quiz_msg))

                    # get user data
                    user_data = None
                    async with database.transaction():
                        query = select(users).where(users.c.id == user_id)
                        user_data = await database.fetch_one(query)     
                    
                    user_email = user_data["user_email"]
                    phone = user_data['user_phone']
                    print("[Notification service] quiz will be sent for user : {} {} ".format(user_id, user_email))

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    app.flashcard_task = asyncio.create_task(ProcessFlashcards())
    app.user_task = asyncio.create_task(ProcessUsers())
    app.quiz_task = asyncio.create_task(ProcessQuizzes())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001,  reload=True, log_level="info")

