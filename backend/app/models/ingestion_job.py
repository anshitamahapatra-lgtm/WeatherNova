from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(80),
    )

    source_name: Mapped[str] = mapped_column(
        String(160),
    )

    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    connector_status: Mapped[str] = mapped_column(
        String(50),
        default="NOT_CONFIGURED",
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="completed",
    )

    records_seen: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    records_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    notes: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
