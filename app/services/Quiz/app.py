import json
from fastapi import FastAPI
from kafka import  KafkaProducer
from config import KAFKA_SERVER, QUIZ_TOPIC
import asyncio
import uvicorn
import schedule


app = FastAPI()
quiz_producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)

def send_quiz_job():
    print("[Quiz Service] Quiz time - sending quiz to other services")
    
    quiz = {"dump_data" : 0}
    quiz_producer.send(QUIZ_TOPIC, json.dumps(quiz).encode("utf-8"))


async def schedule_task():
    print("[Quiz Service] Init schedule task")

    quiz_time = "12:00:00"
    #schedule.every().day.at(quiz_time).do(send_quiz_job)
    schedule.every(30).seconds.do(send_quiz_job)
    
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


@app.on_event("startup")
async def startup():
    app.schedule_task = asyncio.create_task(schedule_task())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8003,  reload=True, log_level="info")