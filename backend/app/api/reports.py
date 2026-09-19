from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import csv
import io
import json

from app.database.connection import get_db
from app.models.report import WeatherReport
from app.ml.report_verification import (
    build_media_metadata,
    dump_json,
    evaluate_report_signals,
    normalize_hashtags,
    normalize_media_urls,
    safe_http_url,
)


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


def serialize_report(report: WeatherReport):
    media_urls = normalize_media_urls(report.media_urls)
    hashtags = normalize_hashtags(report.hashtags)

    try:
        raw_payload = json.loads(report.raw_payload or "{}")
    except json.JSONDecodeError:
        raw_payload = {}

    verification_signals = raw_payload.get(
        "verification_signals",
        {},
    )

    return {
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
        "source_url": report.source_url,
        "media": build_media_metadata(media_urls),
        "media_count": len(media_urls),
        "hashtags": hashtags,
        "verification_notes": report.verification_notes,
        "misinformation_score": report.misinformation_score,
        "verification_signals": verification_signals,
        "timestamp": (
            report.timestamp.isoformat()
            if report.timestamp
            else None
        ),
    }


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

    return [serialize_report(report) for report in reports]


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

    media_urls = normalize_media_urls(report.get("media_urls"))
    hashtags = normalize_hashtags(report.get("hashtags"))
    source_url = safe_http_url(report.get("source_url"))
    verification = evaluate_report_signals(
        db=db,
        source=report.get("source", "WeatherNova"),
        description=report.get("description", ""),
        confidence_score=confidence_score,
        media_urls=media_urls,
    )

    trust_score = max(
        trust_score,
        verification["trust_score"],
    )

    confidence_score = max(
        confidence_score,
        float(report.get("confidence_score", confidence_score)),
    )

    raw_payload = {
        "ingestion": report.get("raw_payload", {}),
        "verification_signals": verification,
        "media_storage": (
            "external_reference_only"
            if media_urls
            else "not_provided"
        ),
    }

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

        confidence_score=confidence_score,

        trust_score=trust_score,

        is_duplicate=report.get(
            "is_duplicate",
            verification["is_duplicate"],
        ),

        source_url=source_url,

        media_urls=dump_json(media_urls),

        hashtags=dump_json(hashtags),

        raw_payload=json.dumps(raw_payload, ensure_ascii=True),

        verification_notes=report.get(
            "verification_notes",
            verification["verification_notes"],
        ),

        misinformation_score=report.get(
            "misinformation_score",
            verification["misinformation_score"],
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
            "source_url",
            "media_count",
            "hashtags",
            "verification_notes",
            "misinformation_score",
            "timestamp",
            "description",
        ]
    )

    for report in reports:
        serialized = serialize_report(report)

        writer.writerow(
            [
                serialized["id"],
                serialized["source"],
                serialized["event_type"],
                serialized["city"],
                serialized["state"],
                serialized["latitude"],
                serialized["longitude"],
                serialized["verification_status"],
                serialized["confidence_score"],
                serialized["trust_score"],
                serialized["is_duplicate"],
                serialized["source_url"],
                serialized["media_count"],
                " ".join(serialized["hashtags"]),
                serialized["verification_notes"],
                serialized["misinformation_score"],
                serialized["timestamp"] or "",
                serialized["description"],
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
