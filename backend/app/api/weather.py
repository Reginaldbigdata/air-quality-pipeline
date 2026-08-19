from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.raw_weather import RawWeather
from app.schemas.weather import WeatherReading

router = APIRouter(prefix="/cities", tags=["weather"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{city_id}/weather", response_model=WeatherReading)
def get_latest_weather(city_id: int, db: Session = Depends(get_db)):
    reading = (
        db.query(RawWeather)
        .filter(RawWeather.city_id == city_id)
        .order_by(RawWeather.recorded_at.desc())
        .first()
    )

    if not reading:
        raise HTTPException(status_code=404, detail=f"No weather data found for city_id {city_id}")

    return reading