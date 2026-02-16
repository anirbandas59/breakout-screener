from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.db.session import Base


class AppConfig(Base):
    """
    Dynamic application configuration stored in the database.

    Used to store values that change without a code deploy,
    such as NSE index URLs.
    """
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
