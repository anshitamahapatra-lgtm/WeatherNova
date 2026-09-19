from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class WeatherReport(Base):
    __tablename__ = "weather_reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(100)
    )

    description: Mapped[str] = mapped_column(
        Text
    )

    event_type: Mapped[str] = mapped_column(
        String(100)
    )

    city: Mapped[str] = mapped_column(
        String(100)
    )

    state: Mapped[str] = mapped_column(
        String(100)
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
    )

    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    trust_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    is_duplicate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(160),
        nullable=True,
        index=True,
    )

    source_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    media_urls: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    hashtags: Mapped[str] = mapped_column(
        Text,
        default="[]",
    )

    raw_payload: Mapped[str] = mapped_column(
        Text,
        default="{}",
    )

    verification_notes: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    misinformation_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
