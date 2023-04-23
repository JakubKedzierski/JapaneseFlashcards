import json
from fastapi import FastAPI
from kafka import KafkaConsumer
from send_email import send_email_async
import asyncio

from config import KAFKA_SERVER, KAFKA_GENERATE_TOPIC
import asyncio
import requests

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

                    # flaschard data
                    user_id = record.value["user_id"]
                    kanji = record.value["kanji"]
                    hiragana = record.value["hiragana"]
                    word = record.value["word"]

                    # request user data
                    get_request = "http://localhost:8002/user/{}".format(user_id)
                    response = requests.get(get_request)
                    
                    # user data
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

                    # send email
                    text_msg = "Here your flaschard: \nhiragana={}, kanji={}, translation={}".format(hiragana, kanji, word)
                    await send_email_async('Flashcard', email, text_msg)

                    # send SMS
                    # if phone present:
                        # send SMS

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    app.flashcard_task = asyncio.create_task(ProcessFlashcards())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001,  reload=True, log_level="info")

