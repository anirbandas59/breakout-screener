import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.config import DATABASE_URL

# Load the DATABASE URL from environment variables
# DATABASE_URL = os.getenv(settings.database_url)
print(settings.database_url)

# SQLAlchemy engine
engine = create_engine(settings.database_url)

# Session Local for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for ORM models
Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
