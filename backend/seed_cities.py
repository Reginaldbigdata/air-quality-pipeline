from app.core.database import SessionLocal
from app.models.city import City
from sqlalchemy.exc import IntegrityError

db = SessionLocal()

cities_to_add = [
    {"name": "Nairobi", "country": "Kenya", "latitude": -1.286389, "longitude": 36.817223, "population": 4397073, "timezone": "Africa/Nairobi"},
    {"name": "Lagos", "country": "Nigeria", "latitude": 6.524379, "longitude": 3.379206, "population": 15388000, "timezone": "Africa/Lagos"},
    {"name": "Cairo", "country": "Egypt", "latitude": 30.044420, "longitude": 31.235712, "population": 10100166, "timezone": "Africa/Cairo"},
    {"name": "Accra", "country": "Ghana", "latitude": 5.603717, "longitude": -0.186964, "population": 2557000, "timezone": "Africa/Accra"},
    {"name": "Kampala", "country": "Uganda", "latitude": 0.347596, "longitude": 32.582520, "population": 1680600, "timezone": "Africa/Kampala"},
    {"name": "Johannesburg", "country": "South Africa", "latitude": -26.204103, "longitude": 28.047305, "population": 5782747, "timezone": "Africa/Johannesburg"},
    {"name": "Kigali", "country": "Rwanda", "latitude": -1.944722, "longitude": 30.061944, "population": 1132686, "timezone": "Africa/Kigali"},
    {"name": "Addis Ababa", "country": "Ethiopia", "latitude": 9.024997, "longitude": 38.741569, "population": 3384569, "timezone": "Africa/Addis_Ababa"},
]

for city_data in cities_to_add:
    existing = db.query(City).filter(
        City.name == city_data["name"], City.country == city_data["country"]
    ).first()

    if existing:
        print(f"⏭️  {city_data['name']} already exists, skipping")
        continue

    city = City(**city_data)
    db.add(city)
    try:
        db.commit()
        db.refresh(city)
        print(f"✅ Inserted city: {city.name} (id={city.id})")
    except IntegrityError:
        db.rollback()
        print(f"⚠️  Could not insert {city_data['name']} (integrity error)")

db.close()