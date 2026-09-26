"""
MedExplain AI - Prediction Record Service

Database service for storing completed MRI prediction results.
"""

from pathlib import Path

from sqlalchemy.orm import Session

from app.models.prediction import Prediction


def create_prediction_record(
    db: Session,
    patient_id: int,
    original_filename: str,
    saved_filename: str,
    image_path: str | Path,
    prediction_result: dict,
    gradcam_result: dict,
) -> Prediction:
    """
    Save one completed MRI analysis to the database.
    """

    visualization = gradcam_result.get(
        "visualization",
        {},
    )

    prediction = Prediction(
        patient_id=patient_id,

        # -----------------------------------------------------
        # Uploaded image
        # -----------------------------------------------------

        original_filename=original_filename,

        saved_filename=saved_filename,

        image_path=str(image_path),

        # -----------------------------------------------------
        # Prediction
        # -----------------------------------------------------

        predicted_class=prediction_result[
            "predicted_class"
        ],

        confidence=float(
            prediction_result["confidence"]
        ),

        confidence_percent=float(
            prediction_result["confidence_percent"]
        ),

        class_probabilities=prediction_result[
            "probabilities"
        ],

        # -----------------------------------------------------
        # Model information
        # -----------------------------------------------------

        feature_dimension=int(
            prediction_result["feature_dimension"]
        ),

        device=str(
            prediction_result["device"]
        ),

        # -----------------------------------------------------
        # Grad-CAM explanation
        # -----------------------------------------------------

        explanation=gradcam_result.get(
            "explanation"
        ),

        original_visualization_path=(
            str(
                visualization["original"]
            )
            if visualization.get("original")
            else None
        ),

        heatmap_visualization_path=(
            str(
                visualization["heatmap"]
            )
            if visualization.get("heatmap")
            else None
        ),

        overlay_visualization_path=(
            str(
                visualization["overlay"]
            )
            if visualization.get("overlay")
            else None
        ),
    )

    db.add(prediction)

    db.commit()

    db.refresh(prediction)

    return prediction