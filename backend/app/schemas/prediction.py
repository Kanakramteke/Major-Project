"""
MedExplain AI - Prediction Schemas

Pydantic schemas for MRI prediction records.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    """
    Response schema for a saved MRI prediction.
    """

    id: int
    patient_id: int

    original_filename: str
    saved_filename: str
    image_path: str

    predicted_class: str
    confidence: float
    confidence_percent: float
    class_probabilities: dict

    feature_dimension: int
    device: str

    explanation: str | None

    original_visualization_path: str | None
    heatmap_visualization_path: str | None
    overlay_visualization_path: str | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )