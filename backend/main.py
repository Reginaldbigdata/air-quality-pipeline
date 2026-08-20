from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.air_quality import router as air_quality_router
from app.api.weather import router as weather_router
from app.core.scheduler import start_scheduler, stop_scheduler
from app.api.diagnostics import router as diagnostics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    start_scheduler()
    yield
    # Runs on shutdown
    stop_scheduler()


app = FastAPI(
    title="African Air Quality Early-Warning System",
    description="Descriptive, diagnostic, predictive, and prescriptive analytics for urban air quality across African cities.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(air_quality_router)
app.include_router(weather_router)
app.include_router(diagnostics_router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Air Quality API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}