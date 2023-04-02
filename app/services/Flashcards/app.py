import json
import sqlite3
from sqlite3 import DatabaseError

from fastapi import FastAPI, BackgroundTasks
from kafka import KafkaConsumer, KafkaProducer

from config import KAFKA_SERVER, KAFKA_FETCH_TOPIC, KAFKA_GENERATE_TOPIC, EXTERNAL_API_WORD, EXTERNAL_API_TRANSLATE
from database import flashcards, database
import asyncio

app = FastAPI()


# async def fetch_word():
#     async with httpx.AsyncClient() as client:
#         response = await client.get(EXTERNAL_API_WORD)
#     return response.json()["word"]


# async def translate_word(word):
#     async with httpx.AsyncClient() as client:
#         response = await client.post(EXTERNAL_API_TRANSLATE, data={"word": word})
#     return response.json()


async def send_flashcard_to_kafka(flashcard):
    # Podłączenie się do Kafki jako producent
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

    # Wysłanie fiszki do Kafki
    producer.send(KAFKA_GENERATE_TOPIC, json.dumps(flashcard).encode("utf-8"))


async def save_flashcard_to_database(flashcard):
    query = flashcards.insert().values(**flashcard)

    await database.execute(query)

    from sqlalchemy import select
    query = select([flashcards])
    await database.fetch_all(query)


async def kafka_fetch_consumer():
    # Podłączenie się do Kafki jako konsument
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

                    # word = await fetch_word()
                    word = 'example'

                    # translations = await translate_word(word)
                    translations = {
                        "hiragana": "ひらがな",
                        "katakana": "カタカナ",
                        "kanji": "漢字",
                        "romaji": "romaji",
                    }

                    flashcard = {"english_word": word, **translations, "user_id": user_id}

                    await send_flashcard_to_kafka(flashcard)
                    await save_flashcard_to_database(flashcard)

        # Czekamy sekundę, żeby nie spaliło komputera
        await asyncio.sleep(1)


# Event z FastAPI na start apki
@app.on_event("startup")
async def startup():
    await database.connect()
    app.kafka_consumer_task = asyncio.create_task(kafka_fetch_consumer())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
