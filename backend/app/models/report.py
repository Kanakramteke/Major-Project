"""
MedExplain AI - Clinical Report Model

Stores clinical reports generated from saved MRI predictions.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    prediction_id: Mapped[int] = mapped_column(
        ForeignKey("predictions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    report_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    report_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    pdf_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )