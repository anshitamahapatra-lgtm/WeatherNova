from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models import WeatherEvent, WeatherReport


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def apply_report_filters(
    query,
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
):
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

    return query


@router.get("/summary")
def analytics_summary(
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # TOTAL REPORTS
    # ---------------------------------------------------------

    total_reports = (
        apply_report_filters(
            db.query(
                WeatherReport
            ),
            event_type,
            state,
            verification_status,
        )
        .with_entities(
            func.count(WeatherReport.id)
        )
        .scalar()
        or 0
    )


    # ---------------------------------------------------------
    # TOTAL EVENTS
    # ---------------------------------------------------------

    total_events = (
        db.query(
            func.count(WeatherEvent.id)
        )
        .scalar()
        or 0
    )


    # ---------------------------------------------------------
    # VERIFIED REPORTS
    # ---------------------------------------------------------

    verified_reports = (
        apply_report_filters(
            db.query(WeatherReport),
            event_type,
            state,
            verification_status,
        )
        .filter(
            WeatherReport.verification_status == "verified"
        )
        .with_entities(func.count(WeatherReport.id))
        .scalar()
        or 0
    )


    # ---------------------------------------------------------
    # DUPLICATE REPORTS
    # ---------------------------------------------------------

    duplicate_reports = (
        apply_report_filters(
            db.query(WeatherReport),
            event_type,
            state,
            verification_status,
        )
        .filter(
            WeatherReport.is_duplicate.is_(True)
        )
        .with_entities(func.count(WeatherReport.id))
        .scalar()
        or 0
    )


    # ---------------------------------------------------------
    # REPORTS BY EVENT TYPE
    # ---------------------------------------------------------

    event_results = (
        apply_report_filters(
            db.query(
                WeatherReport
            ),
            event_type,
            state,
            verification_status,
        )
        .with_entities(
            WeatherReport.event_type,
            func.count(
                WeatherReport.id
            ).label("count"),
        )
        .group_by(
            WeatherReport.event_type
        )
        .all()
    )


    reports_by_event = [
        {
            "event_type": event_type or "Unknown",
            "count": count,
        }
        for event_type, count in event_results
    ]


    # ---------------------------------------------------------
    # REPORTS BY STATE
    # ---------------------------------------------------------

    state_results = (
        apply_report_filters(
            db.query(
                WeatherReport
            ),
            event_type,
            state,
            verification_status,
        )
        .with_entities(
            WeatherReport.state,
            func.count(
                WeatherReport.id
            ).label("count"),
        )
        .group_by(
            WeatherReport.state
        )
        .all()
    )


    reports_by_state = [
        {
            "state": state or "Unknown",
            "count": count,
        }
        for state, count in state_results
    ]


    # ---------------------------------------------------------
    # EVENTS BY SEVERITY
    # ---------------------------------------------------------

    severity_results = (
        db.query(
            WeatherEvent.severity,
            func.count(
                WeatherEvent.id
            ).label("count"),
        )
        .group_by(
            WeatherEvent.severity
        )
        .all()
    )


    events_by_severity = [
        {
            "severity": severity or "Unknown",
            "count": count,
        }
        for severity, count in severity_results
    ]


    # ---------------------------------------------------------
    # RETURN COMPLETE ANALYTICS OBJECT
    # ---------------------------------------------------------

    return {
        "total_reports": total_reports,
        "total_events": total_events,
        "verified_reports": verified_reports,
        "duplicate_reports": duplicate_reports,

        "reports_by_event": reports_by_event,
        "reports_by_state": reports_by_state,
        "events_by_severity": events_by_severity,
    }


# -------------------------------------------------------------
# REPORTS BY EVENT
# -------------------------------------------------------------

@router.get("/reports-by-event")
def reports_by_event(
    state: str | None = None,
    db: Session = Depends(get_db),
):
    results = (
        apply_report_filters(
            db.query(WeatherReport),
            state=state,
        )
        .with_entities(
            WeatherReport.event_type,
            func.count(
                WeatherReport.id
            ).label("count"),
        )
        .group_by(
            WeatherReport.event_type
        )
        .all()
    )

    return [
        {
            "event_type": event_type or "Unknown",
            "count": count,
        }
        for event_type, count in results
    ]


# -------------------------------------------------------------
# REPORTS BY STATE
# -------------------------------------------------------------

@router.get("/reports-by-state")
def reports_by_state(
    event_type: str | None = None,
    db: Session = Depends(get_db),
):
    results = (
        apply_report_filters(
            db.query(WeatherReport),
            event_type=event_type,
        )
        .with_entities(
            WeatherReport.state,
            func.count(
                WeatherReport.id
            ).label("count"),
        )
        .group_by(
            WeatherReport.state
        )
        .all()
    )

    return [
        {
            "state": state or "Unknown",
            "count": count,
        }
        for state, count in results
    ]


# -------------------------------------------------------------
# EVENTS BY SEVERITY
# -------------------------------------------------------------

@router.get("/events-by-severity")
def events_by_severity(
    db: Session = Depends(get_db),
):
    results = (
        db.query(
            WeatherEvent.severity,
            func.count(
                WeatherEvent.id
            ).label("count"),
        )
        .group_by(
            WeatherEvent.severity
        )
        .all()
    )

    return [
        {
            "severity": severity or "Unknown",
            "count": count,
        }
        for severity, count in results
    ]


@router.get("/recent-reports")
def recent_reports(
    limit: int = Query(10, ge=1, le=100),
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    reports = (
        apply_report_filters(
            db.query(WeatherReport),
            event_type,
            state,
            verification_status,
        )
        .order_by(WeatherReport.timestamp.desc())
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
            "confidence_score": report.confidence_score,
            "trust_score": report.trust_score,
            "is_duplicate": report.is_duplicate,
            "timestamp": (
                report.timestamp.isoformat()
                if report.timestamp
                else None
            ),
        }
        for report in reports
    ]


@router.get("/map-reports")
def map_reports(
    event_type: str | None = None,
    state: str | None = None,
    verification_status: str | None = None,
    db: Session = Depends(get_db),
):
    reports = (
        apply_report_filters(
            db.query(WeatherReport),
            event_type,
            state,
            verification_status,
        )
        .filter(WeatherReport.latitude.is_not(None))
        .filter(WeatherReport.longitude.is_not(None))
        .order_by(WeatherReport.timestamp.desc())
        .limit(500)
        .all()
    )

    return [
        {
            "id": report.id,
            "event_type": report.event_type,
            "city": report.city,
            "state": report.state,
            "latitude": report.latitude,
            "longitude": report.longitude,
            "verification_status": (
                report.verification_status
            ),
            "timestamp": (
                report.timestamp.isoformat()
                if report.timestamp
                else None
            ),
        }
        for report in reports
    ]


@router.get("/event-distribution")
def event_distribution(
    state: str | None = None,
    db: Session = Depends(get_db),
):
    return reports_by_event(
        state=state,
        db=db,
    )


@router.get("/location-distribution")
def location_distribution(
    event_type: str | None = None,
    db: Session = Depends(get_db),
):
    return reports_by_state(
        event_type=event_type,
        db=db,
    )
