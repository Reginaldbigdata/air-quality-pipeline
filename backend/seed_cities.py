from app.core.database import SessionLocal
from app.models.city import City

db = SessionLocal()

nairobi = City(
    name="Nairobi",
    country="Kenya",
    latitude=-1.286389,
    longitude=36.817223,
    population=4397073,  # 2019 census, Nairobi County
    timezone="Africa/Nairobi",
)

db.add(nairobi)
db.commit()
db.refresh(nairobi)

print(f"✅ Inserted city: {nairobi.name} (id={nairobi.id})")

db.close()