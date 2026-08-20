from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from scipy.stats import pearsonr
from app.core.database import SessionLocal
from app.models.raw_air_quality import RawAirQuality
from app.models.raw_weather import RawWeather
from app.schemas.diagnostics import FactorCorrelation, DiagnosticResponse

router = APIRouter(prefix="/cities", tags=["diagnostics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def describe_correlation(factor: str, r: float, sample_size: int) -> str:
    strength = "weak"
    if abs(r) >= 0.7:
        strength = "strong"
    elif abs(r) >= 0.4:
        strength = "moderate"

    direction = "higher" if r > 0 else "lower"
    text = f"{strength.capitalize()} relationship: PM2.5 tends to be {direction} when {factor} increases."

    if sample_size < 30:
        text += f" (Note: based on only {sample_size} readings so far — treat as preliminary until more data accumulates.)"

    return text

@router.get("/{city_id}/diagnostics", response_model=DiagnosticResponse)
def get_diagnostics(city_id: int, db: Session = Depends(get_db)):
    aq_rows = db.query(RawAirQuality).filter(
        RawAirQuality.city_id == city_id, RawAirQuality.pm25.isnot(None)
    ).all()
    weather_rows = db.query(RawWeather).filter(RawWeather.city_id == city_id).all()

    if len(aq_rows) < 3 or len(weather_rows) < 3:
        raise HTTPException(
            status_code=400,
            detail="Not enough data yet for diagnostic analysis (need at least 3 matched readings). Check back after more ingestion cycles.",
        )

    aq_df = pd.DataFrame([{"recorded_at": r.recorded_at, "pm25": float(r.pm25)} for r in aq_rows])
    weather_df = pd.DataFrame([{
        "recorded_at": r.recorded_at,
        "temperature": float(r.temperature) if r.temperature is not None else None,
        "humidity": float(r.humidity) if r.humidity is not None else None,
        "wind_speed": float(r.wind_speed) if r.wind_speed is not None else None,
    } for r in weather_rows])

    # Round both to the nearest hour so we can match them up
    aq_df["hour"] = aq_df["recorded_at"].dt.floor("h")
    weather_df["hour"] = weather_df["recorded_at"].dt.floor("h")

    merged = pd.merge(aq_df, weather_df, on="hour", how="inner")

    if len(merged) < 3:
        raise HTTPException(
            status_code=400,
            detail="Not enough matched timestamps between air quality and weather data yet.",
        )

    factors = []
    for factor in ["wind_speed", "temperature", "humidity"]:
        subset = merged[["pm25", factor]].dropna()
        if len(subset) < 3:
            continue
        r, p = pearsonr(subset["pm25"], subset[factor])
        factors.append(FactorCorrelation(
            factor=factor,
            correlation_coefficient=round(r, 4),
            p_value=round(p, 4),
            sample_size=len(subset),
            insight_text=describe_correlation(factor, r, len(subset)),
        ))

    return DiagnosticResponse(city_id=city_id, factors=factors)