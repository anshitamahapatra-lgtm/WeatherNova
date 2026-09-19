import base64
import hashlib
import hmac
import os
import time

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models import AuditLog, Source, WeatherEvent, WeatherReport


router = APIRouter(
    prefix="/admin-api",
    tags=["Admin"],
)


def get_admin_settings():
    return {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "admin"),
        "secret": os.getenv(
            "ADMIN_TOKEN_SECRET",
            "weathernova-local-secret",
        ),
    }


def make_token(username: str):
    settings = get_admin_settings()
    expires_at = int(time.time()) + 60 * 60 * 8
    payload = f"{username}:{expires_at}"
    signature = hmac.new(
        settings["secret"].encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    raw_token = f"{payload}:{signature}"
    return base64.urlsafe_b64encode(
        raw_token.encode("utf-8")
    ).decode("utf-8")


def require_admin(
    authorization: str | None = Header(default=None),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Admin authorization required.",
        )

    token = authorization.replace("Bearer ", "", 1)
    settings = get_admin_settings()

    try:
        decoded = base64.urlsafe_b64decode(
            token.encode("utf-8")
        ).decode("utf-8")
        username, expires_at, signature = decoded.rsplit(":", 2)
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token.",
        ) from exc

    payload = f"{username}:{expires_at}"
    expected_signature = hmac.new(
        settings["secret"].encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin token.",
        )

    if int(expires_at) < int(time.time()):
        raise HTTPException(
            status_code=401,
            detail="Admin token expired.",
        )

    return username


def record_audit(
    db: Session,
    actor: str,
    action: str,
    entity_type: str,
    entity_id: int | None = None,
    details: str = "",
):
    entry = AuditLog(
        actor=actor,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/login")
def admin_login(payload: dict):
    settings = get_admin_settings()

    if (
        payload.get("username") != settings["username"]
        or payload.get("password") != settings["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid admin credentials.",
        )

    return {
        "token": make_token(settings["username"]),
        "token_type": "bearer",
        "expires_in": 60 * 60 * 8,
    }


@router.get("/dashboard")
def admin_dashboard(
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    del actor
    return {
        "pending_reports": db.query(WeatherReport)
        .filter(WeatherReport.verification_status == "pending")
        .count(),
        "verified_reports": db.query(WeatherReport)
        .filter(WeatherReport.verification_status == "verified")
        .count(),
        "rejected_reports": db.query(WeatherReport)
        .filter(WeatherReport.verification_status == "rejected")
        .count(),
        "active_events": db.query(WeatherEvent)
        .filter(WeatherEvent.status == "active")
        .count(),
        "sources": db.query(Source).count(),
        "audit_entries": db.query(AuditLog).count(),
    }


@router.patch("/reports/{report_id}")
def update_report_review(
    report_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    report = db.query(WeatherReport).filter(
        WeatherReport.id == report_id
    ).first()

    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not found.",
        )

    for field in [
        "verification_status",
        "confidence_score",
        "trust_score",
        "is_duplicate",
        "verification_notes",
        "misinformation_score",
    ]:
        if field in payload:
            setattr(report, field, payload[field])

    db.commit()
    db.refresh(report)
    record_audit(
        db,
        actor,
        "review_report",
        "weather_report",
        report.id,
        str(payload),
    )
    return report


@router.patch("/events/{event_id}")
def update_event(
    event_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    event = db.query(WeatherEvent).filter(
        WeatherEvent.id == event_id
    ).first()

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found.",
        )

    for field in [
        "event_type",
        "title",
        "city",
        "state",
        "severity",
        "status",
    ]:
        if field in payload:
            setattr(event, field, payload[field])

    db.commit()
    db.refresh(event)
    record_audit(
        db,
        actor,
        "update_event",
        "weather_event",
        event.id,
        str(payload),
    )
    return event


@router.get("/audit")
def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    del actor
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(min(limit, 250))
        .all()
    )
