"""
Pulls current weather for all active cities from Open-Meteo (free, no API key)
and inserts it into raw_weather.
"""
import sys
import os
sys.path.append(os.getcwd())

import requests
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.models.city import City
from app.models.raw_weather import RawWeather


def fetch_weather_for_city(city: City):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": float(city.latitude),
        "longitude": float(city.longitude),
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,pressure_msl",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()["current"]

    return {
        "temperature": data["temperature_2m"],
        "humidity": data["relative_humidity_2m"],
        "wind_speed": data["wind_speed_10m"],
        "wind_direction": data["wind_direction_10m"],
        "pressure": data["pressure_msl"],
        "recorded_at": datetime.fromisoformat(data["time"]).replace(tzinfo=timezone.utc),
    }


def run():
    db = SessionLocal()
    cities = db.query(City).filter(City.is_active == True).all()


    for city in cities:
        try:
            weather_data = fetch_weather_for_city(city)

            already_exists = db.query(RawWeather).filter(
                RawWeather.city_id == city.id,
                RawWeather.recorded_at == weather_data["recorded_at"],
            ).first()

            if already_exists:
                print(f"⏭️  {city.name}: already have this weather reading")
                continue

            reading = RawWeather(city_id=city.id, **weather_data)
            db.add(reading)
            db.commit()
            print(f"✅ {city.name}: {weather_data['temperature']}°C, wind {weather_data['wind_speed']} km/h")
        except Exception as e:
            db.rollback()
            print(f"❌ Failed for {city.name}: {e}")

    db.close()


if __name__ == "__main__":
    run()