
"""
MedExplain AI - Clinical Reports API

Provides endpoints for generating, retrieving, and listing
AI-assisted clinical reports from saved MRI predictions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_doctor
from app.database.session import get_db
from app.models.doctor import Doctor
from app.schemas.report import ReportResponse
from app.services.report_service import (
    create_report,
    get_doctor_reports,
    get_existing_report,
)

router = APIRouter(
    prefix="/reports",
    tags=["Clinical Reports"],
)


@router.get(
    "/",
    response_model=list[ReportResponse],
)
def list_reports(
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    List clinical reports belonging to the current doctor,
    newest reports first.
    """
    return get_doctor_reports(
        db=db,
        doctor_id=current_doctor.id,
    )


@router.post(
    "/predictions/{prediction_id}",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_report(
    prediction_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Generate an AI-assisted clinical report for a saved
    MRI prediction.

    If a report already exists for the prediction,
    the existing report is returned.
    """
    try:
        return create_report(
            db=db,
            doctor_id=current_doctor.id,
            prediction_id=prediction_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/predictions/{prediction_id}",
    response_model=ReportResponse,
)
def get_report(
    prediction_id: int,
    current_doctor: Doctor = Depends(get_current_doctor),
    db: Session = Depends(get_db),
):
    """
    Retrieve an existing clinical report for a saved
    MRI prediction belonging to the current doctor.
    """
    report = get_existing_report(
        db=db,
        doctor_id=current_doctor.id,
        prediction_id=prediction_id,
    )

    if report is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinical report not found.",
        )

    return report