from pydantic import BaseModel
from typing import Optional


class CityOut(BaseModel):
    id: int
    name: str
    country: str
    latitude: float
    longitude: float
    population: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True