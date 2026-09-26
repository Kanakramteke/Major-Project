"""
MedExplain AI - Authentication Service

Handles doctor registration and authentication.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate


def get_doctor_by_email(
    db: Session,
    email: str,
) -> Doctor | None:
    """
    Find a doctor by email address.
    """
    statement = select(Doctor).where(Doctor.email == email)

    return db.execute(statement).scalar_one_or_none()


def create_doctor(
    db: Session,
    doctor_data: DoctorCreate,
) -> Doctor:
    """
    Create a new doctor account.
    """
    doctor = Doctor(
        full_name=doctor_data.full_name,
        email=doctor_data.email,
        password_hash=hash_password(doctor_data.password),
        specialization=doctor_data.specialization,
    )

    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    return doctor


def authenticate_doctor(
    db: Session,
    email: str,
    password: str,
) -> Doctor | None:
    """
    Authenticate a doctor using email and password.
    """
    doctor = get_doctor_by_email(db, email)

    if doctor is None:
        return None

    if not doctor.is_active:
        return None

    if not verify_password(
        password,
        doctor.password_hash,
    ):
        return None

    return doctor