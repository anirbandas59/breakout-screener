from fastapi import FastAPI
from app.routers import symbols
from app.db.session import Base, engine

# Initialize DB
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include API Routers
app.include_router(symbols.router, prefix="/api")
