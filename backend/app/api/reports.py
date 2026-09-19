from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io

from app.database.connection import get_db
from app.models.report import WeatherReport


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


@router.get("/")
def get_reports(
    limit: int = Query(20, ge=1, le=100),
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(WeatherReport)

    if event_type:
        query = query.filter(
            WeatherReport.event_type == event_type
        )

    if state:
        query = query.filter(
            WeatherReport.state == state
        )

    if verification_status:
        query = query.filter(
            WeatherReport.verification_status
            == verification_status
        )

    reports = (
        query.order_by(WeatherReport.timestamp.desc())
        .limit(limit)
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
    trust_score = float(report.get("trust_score", 0.0))
    confidence_score = float(report.get("confidence_score", 0.0))

    if report.get("source") == "WeatherNova User":
        trust_score = max(trust_score, 0.45)
        confidence_score = max(confidence_score, 0.55)

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
            confidence_score,
        ),

        trust_score=report.get(
            "trust_score",
            trust_score,
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


@router.get("/export")
def export_reports(
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(WeatherReport)

    if event_type:
        query = query.filter(WeatherReport.event_type == event_type)

    if state:
        query = query.filter(WeatherReport.state == state)

    if verification_status:
        query = query.filter(
            WeatherReport.verification_status == verification_status
        )

    reports = query.order_by(WeatherReport.timestamp.desc()).all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id",
            "source",
            "event_type",
            "city",
            "state",
            "latitude",
            "longitude",
            "verification_status",
            "confidence_score",
            "trust_score",
            "is_duplicate",
            "timestamp",
            "description",
        ]
    )

    for report in reports:
        writer.writerow(
            [
                report.id,
                report.source,
                report.event_type,
                report.city,
                report.state,
                report.latitude,
                report.longitude,
                report.verification_status,
                report.confidence_score,
                report.trust_score,
                report.is_duplicate,
                report.timestamp.isoformat() if report.timestamp else "",
                report.description,
            ]
        )

    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=weathernova-reports.csv"
        },
    )
