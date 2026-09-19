from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Source(Base):
    __tablename__ = "weather_sources"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(80),
        default="api",
    )

    reliability_score: Mapped[float] = mapped_column(
        Float,
        default=0.75,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    config_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    auth_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    runtime_status: Mapped[str] = mapped_column(
        String(50),
        default="NOT_CONFIGURED",
    )

    status_notes: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
