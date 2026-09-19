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


@router.get("/")
def get_sources(
    db: Session = Depends(get_db),
):
    sources = db.query(Source).order_by(Source.name.asc()).all()

    if not sources:
        default_sources = [
            Source(
                name="Open-Meteo",
                source_type="weather_api",
                reliability_score=0.95,
                is_active=True,
                last_checked_at=datetime.utcnow(),
            ),
            Source(
                name="Citizen Reports",
                source_type="crowdsourced",
                reliability_score=0.62,
                is_active=True,
            ),
            Source(
                name="Public Datasets",
                source_type="dataset_architecture",
                reliability_score=0.8,
                is_active=False,
            ),
            Source(
                name="Social Media Stream",
                source_type="stream_architecture",
                reliability_score=0.5,
                is_active=False,
            ),
        ]
        db.add_all(default_sources)
        db.commit()
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
