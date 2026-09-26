
"""
MedExplain AI - Prediction History API

Provides previously saved MRI analyses for a patient,
all patients belonging to a doctor, and individual
saved prediction details.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_doctor
from app.database.session import get_db
from app.models.doctor import Doctor
from app.schemas.prediction import PredictionResponse
from app.services.history_service import (
    get_doctor_prediction_history,
    get_patient_prediction_history,
    get_prediction_by_id,
)


router = APIRouter(
    prefix="/history",
    tags=["History"],
)


@router.get("/")
def get_doctor_history(
    current_doctor: Doctor = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db),
):
    """
    Get all previous MRI analyses for the
    currently logged-in doctor's active patients.
    """

    return get_doctor_prediction_history(
        db=db,
        doctor_id=current_doctor.id,
    )


@router.get(
    "/patients/{patient_id}",
    response_model=list[PredictionResponse],
)
def get_patient_history(
    patient_id: int,
    current_doctor: Doctor = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db),
):
    """
    Get all previous MRI analyses for a patient.
    """

    try:
        predictions = get_patient_prediction_history(
            db=db,
            doctor_id=current_doctor.id,
            patient_id=patient_id,
        )

        return predictions

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@router.get(
    "/predictions/{prediction_id}",
    response_model=PredictionResponse,
)
def get_prediction_history_item(
    prediction_id: int,
    current_doctor: Doctor = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db),
):
    """
    Get one previously saved MRI analysis.

    The prediction can only be accessed by the doctor
    who owns the associated patient.
    """

    prediction = get_prediction_by_id(
        db=db,
        doctor_id=current_doctor.id,
        prediction_id=prediction_id,
    )

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found.",
        )

    return prediction