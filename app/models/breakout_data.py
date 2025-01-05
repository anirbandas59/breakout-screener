from sqlalchemy import Column, Integer, String, Float, Date
from app.db.session import Base


class BreakoutData(Base):
    __tablename__ = "breakout_data"

    id = Column(Integer, primary_key=True, index=True)
    script_name = Column(String, index=True)
    group_name = Column(String, index=True)
    date = Column(Date, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    previous_high = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    cpr = Column(Float, nullable=True)
    res1 = Column(Float, nullable=True)
    res2 = Column(Float, nullable=True)
    supp1 = Column(Float, nullable=True)
    supp2 = Column(Float, nullable=True)
    narrow_gap = Column(String, nullable=True)
    breakout_indicator = Column(String, nullable=True)
    candle_indicator = Column(String, nullable=True)
    volume_indicator = Column(String, nullable=True)
    link = Column(String, nullable=True)
