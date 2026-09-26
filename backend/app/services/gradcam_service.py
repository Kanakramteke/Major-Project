"""
MedExplain AI - Grad-CAM Service

Service layer for generating combined Grad-CAM explanations
from the trained feature-fusion model.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Project path setup
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

from ml.explainability.gradcam import FusionGradCAM
from ml.explainability.visualization import (
    save_gradcam_visualization,
)


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

GENERATED_GRADCAM_DIR = (
    PROJECT_ROOT / "backend" / "generated_gradcam"
)

GENERATED_GRADCAM_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ---------------------------------------------------------------------------
# Grad-CAM service
# ---------------------------------------------------------------------------

class GradCAMService:
    """
    Handles Grad-CAM generation for MRI predictions.
    """

    def __init__(self):
        self.gradcam = FusionGradCAM()

    def generate_explanation(
        self,
        image_path: str | Path,
        target_class: str | None = None,
    ) -> dict:
        """
        Generate Grad-CAM visualizations and explanation
        for an MRI image.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # -------------------------------------------------------------------
        # Generate Grad-CAM result from the fusion model.
        #
        # FusionGradCAM returns the individual backbone heatmaps
        # under the key "heatmaps".
        # -------------------------------------------------------------------

        result = self.gradcam.generate(
            image_path=image_path,
            target_class=target_class,
        )

        predicted_class = result["predicted_class"]
        confidence = float(result["confidence"])

        combined_heatmap = result["combined_heatmap"]

        individual_heatmaps = result["heatmaps"]

        # -------------------------------------------------------------------
        # Determine the approximate region with strongest activation.
        #
        # This is an explanatory visualization only and is NOT segmentation.
        # -------------------------------------------------------------------

        height, width = combined_heatmap.shape

        max_position = combined_heatmap.argmax()

        max_y, max_x = divmod(
            max_position,
            width,
        )

        horizontal_position = (
            "left"
            if max_x < width / 3
            else "right"
            if max_x > (2 * width) / 3
            else "central"
        )

        vertical_position = (
            "upper"
            if max_y < height / 3
            else "lower"
            if max_y > (2 * height) / 3
            else "central"
        )

        if (
            horizontal_position == "central"
            and vertical_position == "central"
        ):
            region_description = "central region"
        else:
            region_description = (
                f"{vertical_position}-{horizontal_position} region"
            )

        explanation = (
            f"{predicted_class.replace('_', ' ').title()} predicted "
            f"with {confidence * 100:.2f}% confidence. "
            f"The model's strongest Grad-CAM activation is concentrated "
            f"around the {region_description} of the displayed MRI. "
            f"This visualization indicates image regions that influenced "
            f"the model's prediction and does not represent an exact tumor "
            f"boundary or a clinical diagnosis."
        )

        # -------------------------------------------------------------------
        # Save visualization images
        #
        # Visualization is handled by the dedicated ML visualization module.
        # It uses PIL and NumPy only and does not require Matplotlib/Tkinter.
        # -------------------------------------------------------------------

        visualization = save_gradcam_visualization(
            image_path=image_path,
            heatmap=combined_heatmap,
            predicted_class=predicted_class,
            output_dir=GENERATED_GRADCAM_DIR,
        )

        # -------------------------------------------------------------------
        # Return complete Grad-CAM result
        # -------------------------------------------------------------------

        return {
            "image_path": str(image_path),

            "predicted_class": predicted_class,

            "predicted_class_index": int(
                result["predicted_class_index"]
            ),

            "target_class": result["target_class"],

            "confidence": confidence,

            "confidence_percent": round(
                confidence * 100,
                2,
            ),

            "class_probabilities": result[
                "class_probabilities"
            ],

            "explanation": explanation,

            "combined_heatmap_shape": list(
                combined_heatmap.shape
            ),

            "individual_heatmap_shapes": {
                name: list(heatmap.shape)
                for name, heatmap in individual_heatmaps.items()
            },

            "visualization": visualization,
        }


# ---------------------------------------------------------------------------
# Singleton service
# ---------------------------------------------------------------------------

_gradcam_service = None


def get_gradcam_service() -> GradCAMService:
    """
    Return the shared Grad-CAM service instance.
    """

    global _gradcam_service

    if _gradcam_service is None:
        _gradcam_service = GradCAMService()

    return _gradcam_service