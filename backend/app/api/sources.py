from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.admin import record_audit, require_admin
from app.database.connection import get_db
from app.models import Source


router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


DEFAULT_SOURCES = [
    {
        "name": "Open-Meteo",
        "source_type": "weather_api",
        "reliability_score": 0.95,
        "is_active": True,
        "config_url": "https://api.open-meteo.com",
        "runtime_status": "READY",
        "status_notes": "Existing weather API ingestion is active.",
        "auth_required": False,
    },
    {
        "name": "Citizen Reports",
        "source_type": "crowdsourced",
        "reliability_score": 0.62,
        "is_active": True,
        "config_url": None,
        "runtime_status": "READY",
        "status_notes": "User-submitted report metadata is accepted by WeatherNova.",
        "auth_required": False,
    },
    {
        "name": "Public Datasets",
        "source_type": "public_dataset",
        "reliability_score": 0.8,
        "is_active": False,
        "config_url": None,
        "runtime_status": "NOT_CONFIGURED",
        "status_notes": "Configure PUBLIC_DATASET_URLS to ingest real public datasets.",
        "auth_required": False,
    },
    {
        "name": "Social Media Hashtags",
        "source_type": "social_media",
        "reliability_score": 0.5,
        "is_active": False,
        "config_url": None,
        "runtime_status": "NOT_CONFIGURED",
        "status_notes": "Configure SOCIAL_MEDIA_PROVIDER and SOCIAL_MEDIA_BEARER_TOKEN for real #IMD/weather hashtag ingestion.",
        "auth_required": True,
    },
    {
        "name": "Kafka/Spark Runtime",
        "source_type": "big_data_runtime",
        "reliability_score": 0.75,
        "is_active": False,
        "config_url": None,
        "runtime_status": "NOT_CONFIGURED",
        "status_notes": "Configure Kafka and Spark environment variables before claiming streaming runtime readiness.",
        "auth_required": False,
    },
]


LEGACY_SOURCE_NAMES = {
    "Social Media Stream": "Social Media Hashtags",
}


def ensure_default_sources(db: Session):
    sources = db.query(Source).all()
    by_name = {source.name: source for source in sources}
    changed = False

    for old_name, new_name in LEGACY_SOURCE_NAMES.items():
        if old_name in by_name and new_name not in by_name:
            by_name[old_name].name = new_name
            by_name[new_name] = by_name.pop(old_name)
            changed = True

    for defaults in DEFAULT_SOURCES:
        source = by_name.get(defaults["name"])

        if not source:
            source = Source(**defaults, last_checked_at=datetime.utcnow())
            db.add(source)
            changed = True
            continue

        for field, value in defaults.items():
            if getattr(source, field, None) != value:
                setattr(source, field, value)
                changed = True

        if defaults["runtime_status"] == "READY":
            source.last_checked_at = datetime.utcnow()

    if changed:
        db.commit()


@router.get("/")
def get_sources(
    db: Session = Depends(get_db),
):
    ensure_default_sources(db)
    sources = db.query(Source).order_by(Source.name.asc()).all()

    return sources


@router.post("/")
def create_source(
    payload: dict,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    source = Source(
        name=payload.get("name", "").strip(),
        source_type=payload.get("source_type", "api"),
        reliability_score=float(payload.get("reliability_score", 0.75)),
        is_active=bool(payload.get("is_active", True)),
        last_checked_at=datetime.utcnow(),
    )

    if not source.name:
        raise HTTPException(
            status_code=400,
            detail="Source name is required.",
        )

    db.add(source)
    db.commit()
    db.refresh(source)
    record_audit(
        db,
        actor,
        "create_source",
        "source",
        source.id,
        source.name,
    )
    return source


@router.patch("/{source_id}")
def update_source(
    source_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    actor: str = Depends(require_admin),
):
    source = db.query(Source).filter(Source.id == source_id).first()

    if not source:
        raise HTTPException(
            status_code=404,
            detail="Source not found.",
        )

    for field in [
        "name",
        "source_type",
        "reliability_score",
        "is_active",
        "config_url",
        "auth_required",
        "runtime_status",
        "status_notes",
    ]:
        if field in payload:
            setattr(source, field, payload[field])

    source.last_checked_at = datetime.utcnow()
    db.commit()
    db.refresh(source)
    record_audit(
        db,
        actor,
        "update_source",
        "source",
        source.id,
        str(payload),
    )
    return source
