"""
MedExplain AI - Patient API

Endpoints for creating and retrieving doctor-managed patients.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_doctor
from app.database.session import get_db
from app.models.doctor import Doctor
from app.schemas.patient import PatientCreate, PatientResponse
from app.services.patient_service import (
    create_patient,
    get_patient,
    get_patients,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_patient_endpoint(
    patient_data: PatientCreate,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Create a new patient for the authenticated doctor.
    """

    try:
        return create_patient(
            db=db,
            doctor_id=current_doctor.id,
            patient_data=patient_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[PatientResponse],
)
def get_patients_endpoint(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Get all active patients belonging to the authenticated doctor.
    """

    return get_patients(
        db=db,
        doctor_id=current_doctor.id,
    )


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
def get_patient_endpoint(
    patient_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Get one active patient belonging to the authenticated doctor.
    """

    patient = get_patient(
        db=db,
        doctor_id=current_doctor.id,
        patient_id=patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )

    return patient