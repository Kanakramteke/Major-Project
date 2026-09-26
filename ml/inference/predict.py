"""
MedExplain AI
Reusable inference pipeline for the feature-level fusion model.

The feature extraction logic intentionally matches the
06_feature_fusion.ipynb training pipeline.
"""

from pathlib import Path
import sys

import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from torch import nn


# =========================================================
# Project paths
# =========================================================

ML_DIR = Path(__file__).resolve().parents[1]

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))


from models.backbones import create_all_backbones
from models.feature_fusion import FusionHead
from models.model_config import (
    CLASS_NAMES,
    INDEX_TO_CLASS,
    NORMALIZATION_MEAN,
    NORMALIZATION_STD,
    BACKBONE_FEATURE_DIMENSIONS,
)


PROJECT_ROOT = ML_DIR.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "results"
    / "checkpoints"
    / "feature_fusion"
    / "medexplain_fusion_model.pth"
)


# =========================================================
# Device
# =========================================================

DEVICE = torch.device("cpu")


# =========================================================
# Preprocessing
#
# This intentionally matches Notebook 06:
#
# ToTensor()
# Normalize(mean, std)
#
# No Resize is applied because the processed dataset
# is already 224 x 224.
# =========================================================

IMAGE_TRANSFORM = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(
        mean=NORMALIZATION_MEAN,
        std=NORMALIZATION_STD,
    ),
])


# =========================================================
# MedExplain AI Fusion Model
# =========================================================

class MedExplainFusionModel:

    def __init__(
        self,
        model_path=MODEL_PATH,
        device=DEVICE,
    ):

        self.device = device
        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Fusion model checkpoint not found:\n"
                f"{self.model_path}"
            )

        print(
            "Loading MedExplain AI fusion model..."
        )

        # -------------------------------------------------
        # Load complete fusion package
        # -------------------------------------------------

        checkpoint = torch.load(
            self.model_path,
            map_location=self.device,
            weights_only=False,
        )

        # -------------------------------------------------
        # Create original 4-class backbone architectures
        # -------------------------------------------------

        self.backbones = create_all_backbones()

        backbone_states = checkpoint[
            "backbone_state_dicts"
        ]

        # -------------------------------------------------
        # Load trained backbone weights
        # -------------------------------------------------

        for name, model in self.backbones.items():

            model.load_state_dict(
                backbone_states[name]
            )

            model.to(self.device)

            model.eval()

        # -------------------------------------------------
        # IMPORTANT:
        #
        # Match Notebook 06 exactly.
        #
        # After loading the trained classifier weights,
        # replace the classifier with Identity so that
        # the backbone returns feature vectors.
        # -------------------------------------------------

        self.backbones[
            "efficientnet_b0"
        ].classifier = nn.Identity()

        self.backbones[
            "resnet18"
        ].fc = nn.Identity()

        self.backbones[
            "densenet201"
        ].classifier = nn.Identity()

        self.backbones[
            "mobilenet_v3_large"
        ].classifier = nn.Identity()

        # -------------------------------------------------
        # Create fusion head
        # -------------------------------------------------

        self.fusion_head = FusionHead()

        self.fusion_head.load_state_dict(
            checkpoint[
                "fusion_head_state_dict"
            ]
        )

        self.fusion_head.to(self.device)

        self.fusion_head.eval()

        # -------------------------------------------------
        # Metadata
        # -------------------------------------------------

        self.class_names = checkpoint.get(
            "class_mapping",
            {
                "glioma": 0,
                "meningioma": 1,
                "notumor": 2,
                "pituitary": 3,
            },
        )

        self.feature_dimensions = checkpoint.get(
            "feature_dimensions",
            BACKBONE_FEATURE_DIMENSIONS,
        )

        print(
            "Model loaded successfully."
        )

    # =====================================================
    # Feature Extraction
    # =====================================================

    def extract_features(
        self,
        image_tensor,
    ):
        """
        Extract features exactly as done in Notebook 06.

        Output dimensions:

        EfficientNet-B0      1280
        ResNet-18             512
        DenseNet-201         1920
        MobileNetV3-Large     960
        --------------------------------
        Total                4672
        """

        image_tensor = image_tensor.to(
            self.device
        )

        with torch.no_grad():

            features = [
                self.backbones[
                    "efficientnet_b0"
                ](image_tensor),

                self.backbones[
                    "resnet18"
                ](image_tensor),

                self.backbones[
                    "densenet201"
                ](image_tensor),

                self.backbones[
                    "mobilenet_v3_large"
                ](image_tensor),
            ]

            # Match Notebook 06 exactly.
            combined_features = torch.cat(
                features,
                dim=1,
            )

        return combined_features

    # =====================================================
    # Prediction from Tensor
    # =====================================================

    def predict_tensor(
        self,
        image_tensor,
    ):

        image_tensor = image_tensor.to(
            self.device
        )

        # -------------------------------------------------
        # Extract 4672-dimensional fusion features
        # -------------------------------------------------

        combined_features = (
            self.extract_features(
                image_tensor
            )
        )

        # -------------------------------------------------
        # Verify feature dimension
        # -------------------------------------------------

        expected_dimension = 4672

        actual_dimension = (
            combined_features.shape[1]
        )

        if actual_dimension != expected_dimension:

            raise RuntimeError(
                "Unexpected fusion feature dimension. "
                f"Expected {expected_dimension}, "
                f"got {actual_dimension}."
            )

        # -------------------------------------------------
        # Fusion head
        # -------------------------------------------------

        with torch.no_grad():

            logits = self.fusion_head(
                combined_features
            )

            probabilities = F.softmax(
                logits,
                dim=1,
            )

        # -------------------------------------------------
        # Predicted class
        # -------------------------------------------------

        confidence, predicted_index = torch.max(
            probabilities,
            dim=1,
        )

        predicted_index = (
            predicted_index.item()
        )

        confidence = (
            confidence.item()
        )

        # -------------------------------------------------
        # Class probabilities
        # -------------------------------------------------

        class_probabilities = {
            CLASS_NAMES[index]: float(
                probabilities[
                    0,
                    index
                ].item()
            )
            for index in range(
                len(CLASS_NAMES)
            )
        }

        return {
            "predicted_class": INDEX_TO_CLASS[
                predicted_index
            ],
            "predicted_index": predicted_index,
            "confidence": confidence,
            "class_probabilities": (
                class_probabilities
            ),
        }

    # =====================================================
    # Prediction from Image
    # =====================================================

    def predict_image(
        self,
        image_path,
    ):

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found:\n"
                f"{image_path}"
            )

        # -------------------------------------------------
        # Load image
        # -------------------------------------------------

        image = Image.open(
            image_path
        ).convert("RGB")

        # -------------------------------------------------
        # Apply exact Notebook 06 preprocessing
        # -------------------------------------------------

        image_tensor = IMAGE_TRANSFORM(
            image
        )

        # -------------------------------------------------
        # Add batch dimension
        # -------------------------------------------------

        image_tensor = image_tensor.unsqueeze(
            0
        )

        # -------------------------------------------------
        # Predict
        # -------------------------------------------------

        return self.predict_tensor(
            image_tensor
        )


# =========================================================
# Module Test
# =========================================================

if __name__ == "__main__":

    print(
        "Testing MedExplain AI inference module...\n"
    )

    model = MedExplainFusionModel()

    print()

    print("Backbones loaded:")

    for name in model.backbones:
        print(f"  ✓ {name}")

    print()

    print("Backbone feature dimensions:")

    for name, dimension in (
        BACKBONE_FEATURE_DIMENSIONS.items()
    ):
        print(
            f"  {name}: {dimension}"
        )

    print()

    print(
        "Fusion feature dimension:",
        sum(
            BACKBONE_FEATURE_DIMENSIONS.values()
        ),
    )

    print()

    print(
        "Inference module initialized successfully."
    )