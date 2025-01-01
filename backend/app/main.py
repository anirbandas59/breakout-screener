from fastapi import FastAPI
from app.routes.stocks import router as stocks_router

app = FastAPI()

app.include_router(stocks_router, prefix="/stocks")


@app.get("/")
def home():
    """
    Root path
    """
    return {
        "message": "Backend is running!"
    }
