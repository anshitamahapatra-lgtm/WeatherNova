from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.event import WeatherEvent


router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.get("/")
def get_events(
    db: Session = Depends(get_db),
):
    events = db.query(WeatherEvent).all()

    return events


@router.post("/")
def create_event(
    event: dict,
    db: Session = Depends(get_db),
):
    new_event = WeatherEvent(
        event_type=event.get(
            "event_type",
            "Unknown",
        ),
        title=event.get(
            "title",
            "Weather Event",
        ),
        city=event.get(
            "city",
            "",
        ),
        state=event.get(
            "state",
            "",
        ),
        latitude=event.get(
            "latitude"
        ),
        longitude=event.get(
            "longitude"
        ),
        severity=event.get(
            "severity",
            "unknown",
        ),
        status=event.get(
            "status",
            "active",
        ),
    )

    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    return new_event