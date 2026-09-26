"""
MedExplain AI - Patient Schemas

Pydantic schemas for patient API requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    patient_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=2, max_length=150)
    age: int = Field(..., ge=0, le=120)
    gender: str = Field(..., min_length=1, max_length=20)
    contact: str | None = Field(default=None, max_length=20)
    medical_history: str | None = None


class PatientCreate(PatientBase):
    pass


class PatientResponse(PatientBase):
    id: int
    doctor_id: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }