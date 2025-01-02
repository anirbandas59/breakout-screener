from sqlalchemy import Column, Integer, String, Float, Date
from app.db.session import Base


class BreakoutData(Base):
    __tablename__ = "breakout_data"
    id = Column(Integer, primary_key=True, index=True)
    script_name = Column(String, index=True)
    group_name = Column(String, index=True)
    date = Column(Date, index=True)
    link = Column(String, nullable=True)
    # TODO: Other fields will be added
