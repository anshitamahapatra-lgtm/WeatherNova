from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.admin import router as admin_router
from app.api.reports import router as reports_router
from app.api.alerts import router as alerts_router
from app.api.analytics import router as analytics_router
from app.api.big_data import router as big_data_router
from app.api.events import router as events_router
from app.api.sources import router as sources_router
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
app.include_router(admin_router)
app.include_router(alerts_router)
app.include_router(analytics_router)
app.include_router(big_data_router)
app.include_router(events_router)
app.include_router(sources_router)
app.include_router(weather_router)


FRONTEND_DIST = (
    Path(__file__).resolve().parents[2]
    / "frontend"
    / "dist"
)

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"

    if assets_dir.exists():
        app.mount(
            "/assets",
            StaticFiles(directory=assets_dir),
            name="assets",
        )


@app.get("/")
def root():
    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {
        "message": "WeatherNova API is running"
    }


@app.get("/{full_path:path}", include_in_schema=False)
def serve_spa(full_path: str):
    index_file = FRONTEND_DIST / "index.html"

    if index_file.exists():
        return FileResponse(index_file)

    return {
        "message": "WeatherNova API is running"
    }
