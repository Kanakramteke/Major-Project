"""
MedExplain AI - Prediction API Endpoint

Handles:

    Doctor
      ↓
    Patient
      ↓
    MRI upload
      ↓
    Fusion model prediction
      ↓
    Grad-CAM explanation
      ↓
    Save prediction to PostgreSQL
      ↓
    Application-ready JSON response
"""

from pathlib import Path
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_doctor
from app.database.session import get_db
from app.models.doctor import Doctor
from app.services.gradcam_service import (
    get_gradcam_service,
)
from app.services.patient_service import (
    get_patient,
)
from app.services.prediction_record_service import (
    create_prediction_record,
)
from app.services.prediction_service import (
    get_prediction_service,
)


# =============================================================
# Router
# =============================================================

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


# =============================================================
# Paths
# =============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

UPLOAD_DIRECTORY = (
    PROJECT_ROOT
    / "backend"
    / "uploads"
)

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# =============================================================
# Validation
# =============================================================

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


# =============================================================
# Helper - Convert Grad-CAM paths to browser URLs
# =============================================================

def build_visualization_urls(
    visualization: dict,
) -> dict:
    """
    Convert Grad-CAM filesystem paths into URLs
    that can be accessed by the frontend.
    """

    urls = {}

    for key, path in visualization.items():

        filename = Path(path).name

        urls[key] = (
            f"/generated-gradcam/{filename}"
        )

    return urls


# =============================================================
# Prediction Endpoint
# =============================================================

@router.post("/predict")
async def predict_mri(
    patient_id: int = Form(...),
    file: UploadFile = File(...),
    current_doctor: Doctor = Depends(
        get_current_doctor
    ),
    db: Session = Depends(get_db),
):
    """
    Upload a brain MRI and generate:

    - Tumor classification
    - Confidence score
    - Class probabilities
    - Combined Grad-CAM explanation
    - Database prediction record
    - Browser-accessible Grad-CAM visualization URLs
    """

    # ---------------------------------------------------------
    # 1. Verify patient
    # ---------------------------------------------------------

    patient = get_patient(
        db=db,
        doctor_id=current_doctor.id,
        patient_id=patient_id,
    )

    if patient is None:
        raise HTTPException(
            status_code=404,
            detail="Patient not found.",
        )

    # ---------------------------------------------------------
    # 2. Validate filename
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was provided.",
        )

    original_filename = Path(
        file.filename
    ).name

    extension = Path(
        original_filename
    ).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid file type. "
                "Please upload a JPG, JPEG, or PNG image."
            ),
        )

    # ---------------------------------------------------------
    # 3. Read uploaded file
    # ---------------------------------------------------------

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds the 10 MB limit.",
        )

    # ---------------------------------------------------------
    # 4. Save uploaded image
    # ---------------------------------------------------------

    unique_filename = (
        f"{uuid4().hex}{extension}"
    )

    image_path = (
        UPLOAD_DIRECTORY
        / unique_filename
    )

    try:
        image_path.write_bytes(
            file_bytes
        )

    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save uploaded image: {exc}"
            ),
        )

    # ---------------------------------------------------------
    # 5. Run AI pipeline
    # ---------------------------------------------------------

    try:

        # -----------------------------------------------------
        # Prediction
        # -----------------------------------------------------

        prediction_service = (
            get_prediction_service()
        )

        prediction_result = (
            prediction_service.predict(
                image_path=image_path
            )
        )

        # -----------------------------------------------------
        # Grad-CAM
        # -----------------------------------------------------

        gradcam_service = (
            get_gradcam_service()
        )

        gradcam_result = (
            gradcam_service.generate_explanation(
                image_path=image_path,
                target_class=None,
            )
        )

        # -----------------------------------------------------
        # Save prediction to PostgreSQL
        # -----------------------------------------------------

        prediction_record = (
            create_prediction_record(
                db=db,
                patient_id=patient.id,
                original_filename=(
                    original_filename
                ),
                saved_filename=(
                    unique_filename
                ),
                image_path=image_path,
                prediction_result=(
                    prediction_result
                ),
                gradcam_result=(
                    gradcam_result
                ),
            )
        )

        # -----------------------------------------------------
        # Convert Grad-CAM paths to browser URLs
        # -----------------------------------------------------

        visualization_urls = (
            build_visualization_urls(
                gradcam_result[
                    "visualization"
                ]
            )
        )

        # -----------------------------------------------------
        # Return application response
        # -----------------------------------------------------

        return {
            "success": True,

            "prediction": {
                "id": prediction_record.id,

                "patient_id": patient.id,

                "predicted_class": (
                    prediction_result[
                        "predicted_class"
                    ]
                ),

                "confidence": (
                    prediction_result[
                        "confidence"
                    ]
                ),

                "confidence_percent": (
                    prediction_result[
                        "confidence_percent"
                    ]
                ),

                "class_probabilities": (
                    prediction_result[
                        "probabilities"
                    ]
                ),

                "feature_dimension": (
                    prediction_result[
                        "feature_dimension"
                    ]
                ),

                "device": (
                    prediction_result[
                        "device"
                    ]
                ),
            },

            "patient": {
                "id": patient.id,

                "patient_id": (
                    patient.patient_id
                ),

                "full_name": (
                    patient.full_name
                ),

                "age": patient.age,

                "gender": patient.gender,
            },

            "explainability": {
                "explanation": (
                    gradcam_result[
                        "explanation"
                    ]
                ),

                "combined_heatmap_shape": (
                    gradcam_result[
                        "combined_heatmap_shape"
                    ]
                ),

                "visualization": (
                    visualization_urls
                ),
            },

            "image": {
                "original_filename": (
                    original_filename
                ),

                "saved_filename": (
                    unique_filename
                ),
            },
        }

    except FileNotFoundError as exc:

        db.rollback()

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Prediction pipeline failed: {exc}"
            ),
        )


# =============================================================
# Module test
# =============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("MedExplain AI Prediction API")
    print("=" * 60)

    print()
    print(
        "Prediction endpoint:"
    )

    print(
        "POST /predictions/predict"
    )

    print()
    print(
        "This module is intended to be "
        "used through FastAPI."
    )

    print("=" * 60)