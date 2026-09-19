from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import WeatherEvent, WeatherReport


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get("/")
def get_alerts(
    db: Session = Depends(get_db),
):
    events = (
        db.query(WeatherEvent)
        .filter(WeatherEvent.status == "active")
        .order_by(WeatherEvent.start_time.desc())
        .limit(50)
        .all()
    )

    reports = (
        db.query(WeatherReport)
        .filter(WeatherReport.verification_status == "verified")
        .filter(WeatherReport.event_type != "Clear/Cloudy")
        .order_by(WeatherReport.timestamp.desc())
        .limit(50)
        .all()
    )

    return {
        "active_alerts": [
            {
                "id": event.id,
                "title": event.title,
                "event_type": event.event_type,
                "city": event.city,
                "state": event.state,
                "severity": event.severity,
                "status": event.status,
                "timestamp": event.start_time.isoformat()
                if event.start_time
                else None,
            }
            for event in events
        ],
        "verified_signals": [
            {
                "id": report.id,
                "event_type": report.event_type,
                "city": report.city,
                "state": report.state,
                "trust_score": report.trust_score,
                "timestamp": report.timestamp.isoformat()
                if report.timestamp
                else None,
            }
            for report in reports
        ],
    }
