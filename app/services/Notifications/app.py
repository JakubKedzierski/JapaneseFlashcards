import json
from fastapi import FastAPI
from kafka import KafkaConsumer
from send_email import send_email_async
import asyncio

from config import KAFKA_SERVER, KAFKA_GENERATE_TOPIC
import asyncio

app = FastAPI()


async def ProcessFlashcards():
    consumer = KafkaConsumer(
        KAFKA_GENERATE_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    while True:
        msg = consumer.poll(timeout_ms=5000)
        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    email = record.value["email"]
                    phone = record.value["phone"]

                    print("Notifications: got flashcard user_id: {}, email: {}, phone: {}".format(user_id, email, phone))

                    await send_email_async('Flashcard','flashcard_temp@gmail.com', 'Here your flaschard :)')

                    # if phone present:
                        # send SMS

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    app.flashcard_task = asyncio.create_task(ProcessFlashcards())


if __name__ == "__main__":
    import uvicorn
    print("App Startup")
    uvicorn.run("app:app", host="0.0.0.0", port=8001,  reload=True, log_level="info")

