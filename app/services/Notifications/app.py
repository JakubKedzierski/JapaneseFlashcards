import json
from fastapi import FastAPI
from kafka import KafkaConsumer

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
        msg = consumer.poll(timeout_ms=1000)
        if msg:
            for _, records in msg.items():
                for record in records:
                    user_id = record.value["user_id"]
                    print("Notifications: got flashcard user_id: {}".format(user_id))

                    # Ask for user data

                    # Wait for user data

                    # Send email 

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

