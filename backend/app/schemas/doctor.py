"""
MedExplain AI - Doctor Schemas

Pydantic schemas for doctor-related API requests and responses.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class DoctorBase(BaseModel):
    """
    Common doctor fields.
    """

    full_name: str
    email: EmailStr
    specialization: str | None = None


class DoctorCreate(DoctorBase):
    """
    Data required when registering a doctor.
    """

    password: str


class DoctorResponse(DoctorBase):
    """
    Doctor data returned by the API.

    The password is intentionally excluded.
    """

    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)