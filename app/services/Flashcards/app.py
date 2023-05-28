import json
from random import randint

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from kafka import KafkaConsumer, KafkaProducer
from config import KAFKA_SERVER, KAFKA_FETCH_TOPIC, KAFKA_GENERATE_TOPIC, KAFKA_USER_TOPIC
from database import flashcards, database, users
import asyncio
from jisho_api.word import Word
import uvicorn
from sqlalchemy import select

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# level => 1 or 2 or 3 or 4
async def fetch_word(level):
    response = Word.request("#jlpt-n" + level)
    position = randint(0, len(response.data) - 1)
    data = response.data[position]

    return {
        "kanji": data.japanese[0].word,
        "hiragana": data.japanese[0].reading,
        "word": ", ".join(data.senses[0].english_definitions)
    }


async def send_flashcard_to_kafka(flashcard):
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    message = {**flashcard}
    producer.send(KAFKA_GENERATE_TOPIC, json.dumps(message).encode("utf-8"))


async def save_flashcard_to_database(flashcard):
    query = flashcards.insert().values(**flashcard)
    await database.execute(query)

    print("[Flashcard service] Flashcard saved to db")


@app.get("/flashcard/{level}", status_code=200)
async def send_flashcard(level: str):
    flashcard = await fetch_word(level)

    print("[Flashcard service] Flashcard sent")
    print(flashcard)
    return flashcard


async def process_flashcards():
    consumer = KafkaConsumer(
        KAFKA_FETCH_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Flashcard service] Start processing flashcards \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)

        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    
                    # get user data
                    async with database.transaction():
                        query = select(users).where(users.c.id == user_id)
                        user_data = await database.fetch_one(query)

                    user_id = user_data["id"]
                    user_level = user_data["level"]
                    print("[Flashcard service] get user data from db : id: {} user_level: {} ".format(user_id, user_level))

                    word = await fetch_word(user_level)

                    flashcard = {**word, "user_id": user_id}

                    await send_flashcard_to_kafka(flashcard)
                    await save_flashcard_to_database(flashcard)
                    print(flashcard)

        await asyncio.sleep(1)

async def ProcessUsers():
    consumer = KafkaConsumer(
        KAFKA_USER_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    print("[Flashcard service] Start processing users \n")

    while True:
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    user_level = record.value["level"]

                    print("[Flashcard service] Received user: id: {} level: {} ".format(user_id, user_level))

                    async with database.transaction():
                        user_db = {"id":user_id, "level":user_level}
                        query = users.insert().values(**user_db)
                        await database.execute(query)
                    
                    print("[Flashcard service] user saved to db: {} ".format(user_id))

        await asyncio.sleep(1)

@app.post("/debug_endpoints/send_flashcard/{id}", status_code=200)
async def send_flashcard(id: int):
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    producer.send(KAFKA_FETCH_TOPIC, json.dumps({"user_id":str(id)}).encode("utf-8"))
    return '[Flashcard service] : debug flashcard sent'

@app.on_event("startup")
async def startup():
    await database.connect()
    app.kafka_consumer_task = asyncio.create_task(process_flashcards())
    app.user_task = asyncio.create_task(ProcessUsers())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
