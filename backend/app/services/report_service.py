
"""
MedExplain AI - Clinical Report Service

Creates, retrieves, and lists clinical reports and generates
professional PDF reports for saved predictions.
"""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.report import Report
from app.utils.pdf_generator import generate_clinical_report_pdf


def get_prediction_for_report(
    db: Session,
    doctor_id: int,
    prediction_id: int,
) -> tuple[Prediction, Patient] | None:
    result = db.execute(
        select(Prediction, Patient)
        .join(
            Patient,
            Prediction.patient_id == Patient.id,
        )
        .where(
            Prediction.id == prediction_id,
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
    ).first()

    if result is None:
        return None

    prediction, patient = result
    return prediction, patient


def get_doctor(
    db: Session,
    doctor_id: int,
) -> Doctor | None:
    return db.scalar(
        select(Doctor).where(
            Doctor.id == doctor_id,
            Doctor.is_active.is_(True),
        )
    )


def get_existing_report(
    db: Session,
    doctor_id: int,
    prediction_id: int,
) -> Report | None:
    result = db.execute(
        select(Report)
        .join(
            Prediction,
            Report.prediction_id == Prediction.id,
        )
        .join(
            Patient,
            Prediction.patient_id == Patient.id,
        )
        .where(
            Report.prediction_id == prediction_id,
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
    ).scalar_one_or_none()

    return result


def build_report_text(
    prediction: Prediction,
    patient: Patient,
) -> str:
    probabilities = prediction.class_probabilities

    probability_lines = "\n".join(
        f"- {class_name.title()}: {float(probability) * 100:.2f}%"
        for class_name, probability
        in sorted(
            probabilities.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    explanation = (
        prediction.explanation
        or (
            "Grad-CAM visualization indicates the image regions "
            "that contributed most strongly to the model prediction."
        )
    )

    return (
        "MedExplain AI - Brain Tumor MRI Analysis Report\n\n"
        f"Patient Name: {patient.full_name}\n"
        f"Patient ID: {patient.patient_id}\n"
        f"Age: {patient.age}\n"
        f"Gender: {patient.gender}\n\n"
        "MRI Analysis\n"
        f"Predicted Classification: "
        f"{prediction.predicted_class.title()}\n"
        f"Confidence: {prediction.confidence_percent:.2f}%\n"
        f"Model Feature Dimension: {prediction.feature_dimension}\n"
        f"Inference Device: {prediction.device}\n\n"
        "Class Probabilities\n"
        f"{probability_lines}\n\n"
        "Explainability\n"
        f"{explanation}\n\n"
        "Clinical Note\n"
        "This report is generated using an artificial intelligence "
        "system for research and decision-support purposes. The "
        "prediction and visual explanation should be reviewed by "
        "a qualified medical professional and must not be considered "
        "a standalone clinical diagnosis."
    )


def create_report(
    db: Session,
    doctor_id: int,
    prediction_id: int,
) -> Report:
    existing_report = get_existing_report(
        db=db,
        doctor_id=doctor_id,
        prediction_id=prediction_id,
    )

    prediction_patient = get_prediction_for_report(
        db=db,
        doctor_id=doctor_id,
        prediction_id=prediction_id,
    )

    if prediction_patient is None:
        raise ValueError(
            "Prediction not found or does not belong to the current doctor."
        )

    prediction, patient = prediction_patient

    doctor = get_doctor(
        db=db,
        doctor_id=doctor_id,
    )

    if doctor is None:
        raise ValueError("Doctor not found.")

    # ---------------------------------------------------------
    # Existing report
    # ---------------------------------------------------------
    if existing_report is not None:

        # If the PDF already exists, simply return the report.
        if existing_report.pdf_path:
            pdf_file = Path(existing_report.pdf_path)

            if pdf_file.exists():
                return existing_report

        # Existing database report has no valid PDF.
        # Generate the PDF using the existing report ID.
        pdf_path = generate_clinical_report_pdf(
            report_id=existing_report.id,
            prediction=prediction,
            patient=patient,
            doctor=doctor,
        )

        existing_report.pdf_path = str(pdf_path)

        db.commit()
        db.refresh(existing_report)

        return existing_report

    # ---------------------------------------------------------
    # Create a new report
    # ---------------------------------------------------------
    report_text = build_report_text(
        prediction=prediction,
        patient=patient,
    )

    report_title = (
        f"AI-Assisted Brain MRI Report - "
        f"{patient.patient_id}"
    )

    report = Report(
        prediction_id=prediction.id,
        report_title=report_title,
        report_text=report_text,
        pdf_path=None,
    )

    db.add(report)

    # Generate the database ID before generating the PDF.
    db.flush()

    pdf_path = generate_clinical_report_pdf(
        report_id=report.id,
        prediction=prediction,
        patient=patient,
        doctor=doctor,
    )

    report.pdf_path = str(pdf_path)

    db.commit()
    db.refresh(report)

    return report


def get_doctor_reports(
    db: Session,
    doctor_id: int,
) -> list[Report]:
    """
    Return clinical reports belonging to the current doctor,
    newest reports first.
    """
    reports = db.execute(
        select(Report)
        .join(
            Prediction,
            Report.prediction_id == Prediction.id,
        )
        .join(
            Patient,
            Prediction.patient_id == Patient.id,
        )
        .where(
            Patient.doctor_id == doctor_id,
            Patient.is_active.is_(True),
        )
        .order_by(Report.created_at.desc())
    ).scalars().all()

    return reports