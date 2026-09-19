from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String
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

    last_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
