"""
MedExplain AI - Patient Service

Business logic for creating and retrieving doctor-managed patients.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.schemas.patient import PatientCreate


def create_patient(
    db: Session,
    doctor_id: int,
    patient_data: PatientCreate,
) -> Patient:
    existing_patient = db.scalar(
        select(Patient).where(
            Patient.doctor_id == doctor_id,
            Patient.patient_id == patient_data.patient_id,
            Patient.is_active.is_(True),
        )
    )

    if existing_patient:
        raise ValueError(
            "A patient with this Patient ID already exists."
        )

    patient = Patient(
        doctor_id=doctor_id,
        patient_id=patient_data.patient_id,
        full_name=patient_data.full_name,
        age=patient_data.age,
        gender=patient_data.gender,
        contact=patient_data.contact,
        medical_history=patient_data.medical_history,
    )

    db.add(patient)
    db.commit()
    db.refresh(patient)

    return patient


def get_patients(
    db: Session,
    doctor_id: int,
) -> list[Patient]:
    patients = db.scalars(
        select(Patient)
        .where(
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
        .order_by(Patient.created_at.desc())
    ).all()

    return list(patients)


def get_patient(
    db: Session,
    doctor_id: int,
    patient_id: int,
) -> Patient | None:
    patient = db.scalar(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
    )

    return patient