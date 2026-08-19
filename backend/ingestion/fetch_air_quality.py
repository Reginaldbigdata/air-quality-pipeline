"""
Pulls latest air quality readings for all active cities from OpenAQ v3
and inserts them into raw_air_quality.
"""
import sys
import os
sys.path.append(os.getcwd())

import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from app.core.database import SessionLocal
from app.models.city import City
from app.models.raw_air_quality import RawAirQuality

load_dotenv()
OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
HEADERS = {"X-API-Key": OPENAQ_API_KEY}

PARAM_MAP = {"pm25": "pm25", "pm10": "pm10", "no2": "no2", "o3": "o3"}
STALE_THRESHOLD_DAYS = 7  # ignore stations that haven't reported recently


def find_candidate_locations(lat, lon):
    """Find nearby OpenAQ monitoring locations (25km is OpenAQ's max allowed radius)."""
    url = "https://api.openaq.org/v3/locations"
    params = {"coordinates": f"{lat},{lon}", "radius": 25000, "limit": 20}
    response = requests.get(url, headers=HEADERS, params=params, timeout=10)
    response.raise_for_status()
    return response.json()["results"]


def get_sensor_parameter_map(location_id):
    """Look up which pollutant each sensor at this location measures."""
    url = f"https://api.openaq.org/v3/locations/{location_id}"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    location_data = response.json()["results"][0]

    sensor_map = {}
    for sensor in location_data.get("sensors", []):
        param_name = sensor["parameter"]["name"]
        sensor_map[sensor["id"]] = param_name
    return sensor_map


def fetch_latest_for_location(location_id):
    url = f"https://api.openaq.org/v3/locations/{location_id}/latest"
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.json()["results"]


def pick_active_location(candidates, max_stale_days):
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_stale_days)
    for loc in candidates:
        last_updated_str = loc.get("datetimeLast", {}).get("utc") if loc.get("datetimeLast") else None
        if not last_updated_str:
            continue
        last_updated = datetime.fromisoformat(last_updated_str.replace("Z", "+00:00"))
        if last_updated >= cutoff:
            return loc
    return None


def run():
    db = SessionLocal()
    cities = db.query(City).filter(City.is_active == True).all()

    for city in cities:
        try:
            candidates = find_candidate_locations(float(city.latitude), float(city.longitude))
            if not candidates:
                print(f"⚠️  No OpenAQ stations found near {city.name}")
                continue

            location = None
            for max_stale_days in [7, 30, 90]:
                location = pick_active_location(candidates, max_stale_days)
                if location:
                    if max_stale_days > 7:
                        print(f"ℹ️  {city.name}: using a station last updated within {max_stale_days} days (none fresher found)")
                    break

            if not location:
                print(f"⚠️  No station near {city.name} has reported in the last 90 days (found {len(candidates)} stations, all older)")
                continue

            sensor_map = get_sensor_parameter_map(location["id"])
            latest_readings = fetch_latest_for_location(location["id"])

            values = {}
            recorded_at = None
            for reading in latest_readings:
                param_name = sensor_map.get(reading["sensorsId"])
                if param_name in PARAM_MAP:
                    values[PARAM_MAP[param_name]] = reading["value"]
                    recorded_at = reading["datetime"]["utc"]

            if not recorded_at:
                print(f"⚠️  Station found for {city.name} but no matching pollutants (pm25/pm10/no2/o3)")
                continue

            # Skip if we already have this exact reading (avoids noisy duplicate-key errors on re-run)
            recorded_at_dt = datetime.fromisoformat(recorded_at.replace("Z", "+00:00"))
            already_exists = db.query(RawAirQuality).filter(
                RawAirQuality.city_id == city.id,
                RawAirQuality.source == "openaq",
                RawAirQuality.recorded_at == recorded_at_dt,
            ).first()

            if already_exists:
                print(f"⏭️  {city.name}: already have this reading (station hasn't updated since last run)")
                continue

            entry = RawAirQuality(
                city_id=city.id,
                source="openaq",
                pm25=values.get("pm25"),
                pm10=values.get("pm10"),
                no2=values.get("no2"),
                o3=values.get("o3"),
                recorded_at=recorded_at_dt,
            )
            db.add(entry)
            db.commit()
            print(f"✅ {city.name} (station: {location['name']}): PM2.5={values.get('pm25')}, PM10={values.get('pm10')}")

        except Exception as e:
            db.rollback()
            print(f"❌ Failed for {city.name}: {e}")

    db.close()


if __name__ == "__main__":
    run()