from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class RawAirQuality(Base):
    __tablename__ = "raw_air_quality"

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    source = Column(String(20), nullable=False)  # 'openaq' or 'airqo'
    pm25 = Column(Numeric(6, 2))
    pm10 = Column(Numeric(6, 2))
    no2 = Column(Numeric(6, 2))
    o3 = Column(Numeric(6, 2))
    aqi = Column(Integer)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("city_id", "source", "recorded_at", name="uq_air_quality_reading"),
    )