import json
from fastapi import FastAPI
from pydantic import BaseModel
from database import users, database
from sqlalchemy import select


app = FastAPI()


class User(BaseModel):
    user_email: str
    user_phone: str | None = None
    token: str 

async def save_user_to_database(user):
    async with database.transaction():
        query = users.insert().values(**user)
        await database.execute(query)

    print("User saved to DB")


@app.post("/user/add_user", status_code=200)
async def add_user(user: User):
    user_db = {"user_email":user.user_email, "user_phone":user.user_phone, "token":user.token}
    await save_user_to_database(user_db)
    return user

@app.get("/user/{user_id}", status_code=200)
async def get_user_data(user_id: int):
    async with database.transaction():
        query = select(users).where(users.c.id == user_id)
        x = await database.fetch_one(query)

    return x

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002,  reload=True, log_level="info")

