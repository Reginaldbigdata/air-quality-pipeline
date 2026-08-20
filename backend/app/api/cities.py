from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.models.city import City
from app.schemas.city import CityOut

router = APIRouter(prefix="/cities", tags=["cities"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=List[CityOut])
def list_cities(db: Session = Depends(get_db)):
    return db.query(City).filter(City.is_active == True).all()