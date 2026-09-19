from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.reports import router as reports_router
from app.api.analytics import router as analytics_router
from app.api.events import router as events_router
from app.api.weather import router as weather_router
from app.database.init_db import init_db


app = FastAPI(
    title="WeatherNova API",
    description="Weather intelligence and analytics API",
    version="1.0.0",
)


@app.on_event("startup")
def startup_event():
    init_db()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "https://weathernova-4.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(reports_router)
app.include_router(analytics_router)
app.include_router(events_router)
app.include_router(weather_router)


@app.get("/")
def root():
    return {
        "message": "WeatherNova API is running"
    }