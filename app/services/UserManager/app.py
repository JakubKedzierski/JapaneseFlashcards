import json
from fastapi import FastAPI


app = FastAPI()


@app.get("/user/{user_id}", status_code=200)
def get_user_data(user_id: int):
    return str({"user" : user_id})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002,  reload=True, log_level="info")

