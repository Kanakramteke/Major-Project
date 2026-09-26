
"""
MedExplain AI - Prediction Model

Database model for storing MRI analysis results
associated with a patient.
"""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class Prediction(Base):
    """
    Stores one completed MRI analysis.
    """

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    # ---------------------------------------------------------
    # Uploaded MRI information
    # ---------------------------------------------------------

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    saved_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    image_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Prediction information
    # ---------------------------------------------------------

    predicted_class: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    confidence_percent: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    class_probabilities: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Model information
    # ---------------------------------------------------------

    feature_dimension: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    device: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # ---------------------------------------------------------
    # Explainability information
    # ---------------------------------------------------------

    explanation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    original_visualization_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    heatmap_visualization_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    overlay_visualization_path: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Timestamp
    # ---------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
