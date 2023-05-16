import json
from fastapi import FastAPI
from pydantic import BaseModel
from database import users, database
from sqlalchemy import select
from kafka import KafkaProducer
from config import KAFKA_SERVER, KAFKA_USER_TOPIC

app = FastAPI()


class User(BaseModel):
    user_email: str
    user_phone: str | None = None
    token: str 

async def save_user_to_database(user):
    async with database.transaction():
        query = users.insert().values(**user)
        result = await database.execute(query)
        user_id = result

    print("User {} saved to DB".format(user_id))
    return user_id


@app.post("/user/add_user", status_code=200)
async def add_user(user: User):
    user_db = {"user_email":user.user_email, "user_phone":user.user_phone, "token":user.token}
    user_id = await save_user_to_database(user_db)

    user_kaffka = {"user_id": user_id, "user_email":user.user_email, "user_phone":user.user_phone, "token":user.token}
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    producer.send(KAFKA_USER_TOPIC, json.dumps(user_kaffka).encode("utf-8"))
    
    return user

# just for debugging purpose
@app.get("/user/{user_id}", status_code=200)
async def get_user_data(user_id: int):
    async with database.transaction():
        query = select(users).where(users.c.id == user_id)
        x = await database.fetch_one(query)

    return x

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002,  reload=True, log_level="info")

