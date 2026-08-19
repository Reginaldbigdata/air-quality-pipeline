from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AirQualityReading(BaseModel):
    city_id: int
    source: str
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    recorded_at: datetime

    class Config:
        from_attributes = True  # lets Pydantic read directly from SQLAlchemy model objects