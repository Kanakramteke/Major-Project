"""
MedExplain AI - Clinical Report Schemas
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    id: int
    prediction_id: int
    report_title: str
    report_text: str
    pdf_path: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )