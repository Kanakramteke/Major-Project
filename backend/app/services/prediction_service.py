"""
MedExplain AI - Prediction Service

Application-level service for running brain MRI predictions
using the trained feature-level fusion model.

Workflow:
    MRI
      ↓
    Preprocessing
      ↓
    EfficientNet-B0 ───────┐
    ResNet-18              │
    DenseNet-201           ├──→ 4672-d feature vector
    MobileNetV3-Large ─────┘
      ↓
    Fusion Head
      ↓
    Prediction
"""

from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F

from app.ml.model_loader import get_model_loader
from app.ml.preprocessing import preprocess_image


class PredictionService:
    """Run predictions using the trained MedExplain AI fusion model."""

    def __init__(self) -> None:
        self.model_loader = get_model_loader()

        self.device = self.model_loader.get_device()
        self.class_names = self.model_loader.get_class_names()
        self.backbones = self.model_loader.get_backbones()
        self.fusion_head = self.model_loader.get_fusion_head()
        self.feature_dims = self.model_loader.get_feature_dims()

    def _extract_features(
        self,
        image_tensor: torch.Tensor,
    ) -> list[torch.Tensor]:
        """
        Extract the exact feature representations used during
        feature-level fusion training.
        """

        features = []

        with torch.no_grad():

            # -------------------------------------------------
            # EfficientNet-B0
            # -------------------------------------------------
            efficientnet = self.backbones["efficientnet_b0"]
            efficientnet.eval()

            x = efficientnet.features(image_tensor)
            x = efficientnet.avgpool(x)
            x = torch.flatten(x, 1)

            features.append(x)

            # -------------------------------------------------
            # ResNet-18
            # -------------------------------------------------
            resnet = self.backbones["resnet18"]
            resnet.eval()

            x = resnet.conv1(image_tensor)
            x = resnet.bn1(x)
            x = resnet.relu(x)
            x = resnet.maxpool(x)

            x = resnet.layer1(x)
            x = resnet.layer2(x)
            x = resnet.layer3(x)
            x = resnet.layer4(x)

            x = resnet.avgpool(x)
            x = torch.flatten(x, 1)

            features.append(x)

            # -------------------------------------------------
            # DenseNet-201
            # -------------------------------------------------
            densenet = self.backbones["densenet201"]
            densenet.eval()

            x = densenet.features(image_tensor)

            x = F.relu(x, inplace=False)

            x = F.adaptive_avg_pool2d(
                x,
                (1, 1),
            )

            x = torch.flatten(x, 1)

            features.append(x)

            # -------------------------------------------------
            # MobileNetV3-Large
            # -------------------------------------------------
            mobilenet = self.backbones["mobilenet_v3_large"]
            mobilenet.eval()

            x = mobilenet.features(image_tensor)

            x = mobilenet.avgpool(x)

            x = torch.flatten(x, 1)

            features.append(x)

        return features

    def predict(
        self,
        image_path: str | Path,
    ) -> dict[str, Any]:
        """
        Run prediction on one MRI image.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"MRI image not found: {image_path}"
            )

        # -----------------------------------------------------
        # 1. Preprocess image
        # -----------------------------------------------------
        image_tensor = preprocess_image(image_path)
        image_tensor = image_tensor.to(self.device)

        # -----------------------------------------------------
        # 2. Extract backbone features
        # -----------------------------------------------------
        features = self._extract_features(image_tensor)

        # -----------------------------------------------------
        # 3. Validate individual feature dimensions
        # -----------------------------------------------------
        feature_names = [
            "efficientnet_b0",
            "resnet18",
            "densenet201",
            "mobilenet_v3_large",
        ]

        for name, feature in zip(feature_names, features):

            expected = self.feature_dims[name]
            actual = feature.shape[1]

            if actual != expected:
                raise RuntimeError(
                    f"{name} feature dimension mismatch. "
                    f"Expected {expected}, got {actual}."
                )

        # -----------------------------------------------------
        # 4. Concatenate all features
        # -----------------------------------------------------
        fusion_features = torch.cat(
            features,
            dim=1,
        )

        expected_dimension = sum(
            self.feature_dims.values()
        )

        actual_dimension = fusion_features.shape[1]

        if actual_dimension != expected_dimension:
            raise RuntimeError(
                "Fusion feature dimension mismatch. "
                f"Expected {expected_dimension}, "
                f"got {actual_dimension}."
            )

        # -----------------------------------------------------
        # 5. Fusion head prediction
        # -----------------------------------------------------
        self.fusion_head.eval()

        with torch.no_grad():

            logits = self.fusion_head(
                fusion_features
            )

            probabilities = F.softmax(
                logits,
                dim=1,
            )

            predicted_index = torch.argmax(
                probabilities,
                dim=1,
            ).item()

            confidence = probabilities[
                0,
                predicted_index,
            ].item()

        # -----------------------------------------------------
        # 6. Class probabilities
        # -----------------------------------------------------
        probability_dict = {
            class_name: float(
                probabilities[0, index].item()
            )
            for index, class_name in enumerate(
                self.class_names
            )
        }

        probability_dict = dict(
            sorted(
                probability_dict.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

        predicted_class = self.class_names[
            predicted_index
        ]

        # -----------------------------------------------------
        # 7. Return result
        # -----------------------------------------------------
        return {
            "predicted_class": predicted_class,
            "confidence": float(confidence),
            "confidence_percent": round(
                float(confidence) * 100,
                2,
            ),
            "probabilities": probability_dict,
            "feature_dimension": int(
                actual_dimension
            ),
            "device": str(self.device),
        }


# =============================================================
# Singleton
# =============================================================

_prediction_service: PredictionService | None = None


def get_prediction_service() -> PredictionService:
    """Return the shared prediction service."""

    global _prediction_service

    if _prediction_service is None:
        _prediction_service = PredictionService()

    return _prediction_service


# =============================================================
# Standalone test
# =============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("Testing MedExplain AI Prediction Service")
    print("=" * 60)

    project_root = Path(__file__).resolve().parents[3]

    test_image = (
        project_root
        / "ml"
        / "data"
        / "processed"
        / "Testing"
        / "pituitary"
        / "Te-pi_1.png"
    )

    print()
    print(f"Test image: {test_image}")

    service = get_prediction_service()

    result = service.predict(test_image)

    print()
    print("Prediction successful.")
    print()
    print(
        f"Predicted class  : "
        f"{result['predicted_class']}"
    )
    print(
        f"Confidence       : "
        f"{result['confidence_percent']:.2f}%"
    )
    print(
        f"Feature dimension: "
        f"{result['feature_dimension']}"
    )
    print(
        f"Device           : "
        f"{result['device']}"
    )

    print()
    print("Class probabilities:")

    for class_name, probability in (
        result["probabilities"].items()
    ):
        print(
            f"  {class_name:<12}: "
            f"{probability * 100:.2f}%"
        )

    print()
    print("PREDICTION SERVICE TEST PASSED")
    print("=" * 60)