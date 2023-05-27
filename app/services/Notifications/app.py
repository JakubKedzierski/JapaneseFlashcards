import json
from fastapi import FastAPI
from kafka import KafkaConsumer
from send_email import send_email_async
from send_sms import send_sms
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

                    try:
                        async with database.transaction():
                            user_db = {"id":user_id, "user_email":user_email, "user_phone":user_phone}
                            query = users.insert().values(**user_db)
                            await database.execute(query)

                        print("[Notification service] user saved to db: {} ".format(user_id))
                    except Exception as e:
                        print("[Notification service] failed to save user in DB : {}".format(e))

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

                    # send email
                    text_msg = "Here your flaschard: \nhiragana={}, kanji={}, translation={}".format(hiragana, kanji, word)
                    try:
                        await send_email_async('Flashcard', user_email, text_msg)
                        print("[Notification service] flashcard email sent for user id: : {} email: {} ".format(user_id, user_email))
                    except Exception as e:
                        print("[Notification service] Sending email has failed. Probably bad email. Error: {}".format(e))


                    # send SMS
                    #sms
                    if phone:
                        msg = "SMS to +{} \n".format(phone) + text_msg
                        try:
                            send_sms(msg)
                        except:
                            print("[Notifications service] Sending sms has failed. Probably bad phone number.")
                    else:
                        print("[Notifications service] No phone provided.")

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
                    print("[Notification service] quiz will be sent for user : {} {} {}".format(user_id, user_email, phone))

                    try:
                        await send_email_async('Quiz', user_email, quiz_msg)
                        print("[Notification service] quiz email sent for user id: : {} email: {} ".format(user_id, user_email))
                    except Exception as e:
                        print("[Notification service] Sending email has failed. Probably bad email. Error: {}".format(e))
                                        
                    #sms
                    if phone:
                        msg = "SMS to +{} \n".format(phone) + quiz_msg
                        try:
                            send_sms(msg)
                        except:
                            print("[Notifications service] Sending sms has failed.")
                    else:
                        print("[Notifications service] No phone provided.")

        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    app.flashcard_task = asyncio.create_task(ProcessFlashcards())
    app.user_task = asyncio.create_task(ProcessUsers())
    app.quiz_task = asyncio.create_task(ProcessQuizzes())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001,  reload=True, log_level="info")

