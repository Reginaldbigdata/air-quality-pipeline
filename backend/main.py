from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.air_quality import router as air_quality_router
from app.api.weather import router as weather_router

app = FastAPI(
    title="African Air Quality Early-Warning System",
    description="Descriptive, diagnostic, predictive, and prescriptive analytics for urban air quality across African cities.",
    version="0.1.0",
)

app.include_router(air_quality_router)
app.include_router(weather_router)

# Allow our future frontend (plain HTML/JS) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we'll tighten this later once frontend is live
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok", "message": "Air Quality API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}