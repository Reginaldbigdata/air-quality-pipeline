"""
Background scheduler that keeps ingestion running automatically.
Starts when the FastAPI app starts, stops when it shuts down.
"""
from apscheduler.schedulers.background import BackgroundScheduler
import sys
import os

sys.path.append(os.getcwd())

scheduler = BackgroundScheduler()


def run_weather_ingestion():
    from ingestion.fetch_weather import run as fetch_weather_run
    print("🔄 Running scheduled weather ingestion...")
    fetch_weather_run()


def run_air_quality_ingestion():
    from ingestion.fetch_air_quality import run as fetch_aq_run
    print("🔄 Running scheduled air quality ingestion...")
    fetch_aq_run()


def start_scheduler():
    # Baseline: every hour, as decided earlier
    scheduler.add_job(run_weather_ingestion, "interval", minutes=60, id="weather_job")
    scheduler.add_job(run_air_quality_ingestion, "interval", minutes=60, id="air_quality_job")
    scheduler.start()
    print("✅ Scheduler started — ingestion will run every 60 minutes.")


def stop_scheduler():
    scheduler.shutdown()