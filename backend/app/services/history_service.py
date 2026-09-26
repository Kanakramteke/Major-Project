
"""
MedExplain AI - History Service

Database service for retrieving previous MRI prediction records
for a patient, a specific prediction, or a doctor's patients.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.prediction import Prediction


def get_patient_prediction_history(
    db: Session,
    doctor_id: int,
    patient_id: int,
) -> list[Prediction]:
    """
    Return all saved MRI predictions for a patient.

    The patient must belong to the currently logged-in doctor.
    """

    patient = db.scalar(
        select(Patient).where(
            Patient.id == patient_id,
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
    )

    if patient is None:
        raise ValueError("Patient not found.")

    predictions = db.scalars(
        select(Prediction)
        .where(
            Prediction.patient_id == patient.id
        )
        .order_by(
            Prediction.created_at.desc()
        )
    ).all()

    return list(predictions)


def get_prediction_by_id(
    db: Session,
    doctor_id: int,
    prediction_id: int,
) -> Prediction | None:
    """
    Return one saved prediction.

    The prediction is returned only when its patient belongs
    to the currently logged-in doctor.
    """

    prediction = db.scalar(
        select(Prediction)
        .join(
            Patient,
            Prediction.patient_id == Patient.id,
        )
        .where(
            Prediction.id == prediction_id,
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
    )

    return prediction


def get_doctor_prediction_history(
    db: Session,
    doctor_id: int,
) -> list[dict]:
    """
    Return all saved MRI predictions belonging to the
    currently logged-in doctor's active patients.

    Newest predictions are returned first.
    """

    results = db.execute(
        select(
            Prediction,
            Patient,
        )
        .join(
            Patient,
            Prediction.patient_id == Patient.id,
        )
        .where(
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
        .order_by(
            Prediction.created_at.desc()
        )
    ).all()

    history = []

    for prediction, patient in results:
        history.append(
            {
                "id": prediction.id,
                "patient_id": patient.id,
                "patient_code": patient.patient_id,
                "patient_name": patient.full_name,
                "original_filename": prediction.original_filename,
                "predicted_class": prediction.predicted_class,
                "confidence_percent": prediction.confidence_percent,
                "created_at": prediction.created_at,
            }
        )

    return history