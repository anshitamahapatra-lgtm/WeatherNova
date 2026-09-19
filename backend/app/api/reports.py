from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.report import WeatherReport


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/")
def get_reports(
    db: Session = Depends(get_db),
):
    reports = (
        db.query(WeatherReport)
        .order_by(
            WeatherReport.timestamp.desc()
        )
        .limit(20)
        .all()
    )

    return [
        {
            "id": report.id,
            "source": report.source,
            "description": report.description,
            "event_type": report.event_type,
            "city": report.city,
            "state": report.state,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "verification_status": (
                report.verification_status
            ),
            "confidence_score": (
                report.confidence_score
            ),
            "trust_score": (
                report.trust_score
            ),
            "is_duplicate": (
                report.is_duplicate
            ),
            "timestamp": (
                report.timestamp.isoformat()
                if report.timestamp
                else None
            ),
        }
        for report in reports
    ]


@router.post("/")
def create_report(
    report: dict,
    db: Session = Depends(get_db),
):
    new_report = WeatherReport(
        source=report.get(
            "source",
            "WeatherNova",
        ),

        description=report.get(
            "description",
            "",
        ),

        event_type=report.get(
            "event_type",
            "Unknown",
        ),

        city=report.get(
            "city",
            "",
        ),

        state=report.get(
            "state",
            "",
        ),

        latitude=report.get(
            "latitude"
        ),

        longitude=report.get(
            "longitude"
        ),

        verification_status=report.get(
            "verification_status",
            "pending",
        ),

        confidence_score=report.get(
            "confidence_score",
            0.0,
        ),

        trust_score=report.get(
            "trust_score",
            0.0,
        ),

        is_duplicate=report.get(
            "is_duplicate",
            False,
        ),
    )

    db.add(new_report)

    db.commit()

    db.refresh(new_report)

    return {
        "id": new_report.id,
        "message": "Weather report created successfully.",
    }