from fastapi import FastAPI


app = FastAPI(title="Test App")

@app.get("/")
def read_root():
    return "Hello World"