from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    actor: Mapped[str] = mapped_column(
        String(120),
        default="system",
    )

    action: Mapped[str] = mapped_column(
        String(120),
    )

    entity_type: Mapped[str] = mapped_column(
        String(80),
    )

    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    details: Mapped[str] = mapped_column(
        Text,
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )
