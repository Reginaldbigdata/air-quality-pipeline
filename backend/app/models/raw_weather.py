from sqlalchemy import Column, Integer, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class RawWeather(Base):
    __tablename__ = "raw_weather"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    temperature = Column(Numeric(5, 2))
    humidity = Column(Numeric(5, 2))
    wind_speed = Column(Numeric(5, 2))
    wind_direction = Column(Numeric(5, 2))
    pressure = Column(Numeric(6, 2))
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("city_id", "recorded_at", name="uq_weather_reading"),
    )