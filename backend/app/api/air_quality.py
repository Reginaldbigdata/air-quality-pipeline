from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.raw_air_quality import RawAirQuality
from app.schemas.air_quality import AirQualityReading

router = APIRouter(prefix="/cities", tags=["air-quality"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{city_id}/air-quality", response_model=AirQualityReading)
def get_latest_air_quality(city_id: int, db: Session = Depends(get_db)):
    reading = (
        db.query(RawAirQuality)
        .filter(RawAirQuality.city_id == city_id)
        .order_by(RawAirQuality.recorded_at.desc())
        .first()
    )

    if not reading:
        raise HTTPException(status_code=404, detail=f"No air quality data found for city_id {city_id}")

    return reading