import json
from random import randint

from fastapi import FastAPI
from kafka import KafkaConsumer, KafkaProducer
from config import KAFKA_SERVER, KAFKA_FETCH_TOPIC, KAFKA_GENERATE_TOPIC
from database import flashcards, database
import asyncio
from jisho_api.word import Word
import uvicorn

app = FastAPI()


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


async def send_flashcard_to_kafka(flashcard, user_phone, user_email):
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    message = {**flashcard, "user_phone": user_phone, "user_email": user_email}
    producer.send(KAFKA_GENERATE_TOPIC, json.dumps(message).encode("utf-8"))


async def save_flashcard_to_database(flashcard):
    query = flashcards.insert().values(**flashcard)
    await database.execute(query)

    # <usunac>
    from sqlalchemy import select
    query = select([flashcards])
    x = await database.fetch_all(query)
    print("Flashcard saved to db: {}".format(x))
    # </usunac>



async def kafka_fetch_consumer():
    consumer = KafkaConsumer(
        KAFKA_FETCH_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    while True:
        msg = consumer.poll(timeout_ms=1000)

        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    level = record.value["level"]
                    user_phone = record.value["user_phone"]
                    user_email = record.value["user_email"]

                    word = await fetch_word(level)

                    flashcard = {**word, "user_id": user_id}

                    await send_flashcard_to_kafka(flashcard, user_phone, user_email)
                    await save_flashcard_to_database(flashcard)
                    print(flashcard)

        await asyncio.sleep(1)

@app.post("/debug_endpoints/send_flashcard", status_code=200)
async def send_flashcard():
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    user_id = 19
    producer.send(KAFKA_FETCH_TOPIC, json.dumps({"user_id":str(user_id),
                                                 "level" : str(1),
                                                 "user_email":"example@aa",
                                                 "user_phone": 123123123
                                                 }).encode("utf-8"))
    return 'FLASHCARD SENT'

@app.on_event("startup")
async def startup():
    await database.connect()
    app.kafka_consumer_task = asyncio.create_task(kafka_fetch_consumer())


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
