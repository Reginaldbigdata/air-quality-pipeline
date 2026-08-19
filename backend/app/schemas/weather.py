from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class WeatherReading(BaseModel):
    city_id: int
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    pressure: Optional[float] = None
    recorded_at: datetime

    class Config:
        from_attributes = True