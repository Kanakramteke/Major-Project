"""
MedExplain AI
Grad-CAM explainability for the feature-level fusion model.

Backbones:
    - EfficientNet-B0
    - ResNet-18
    - DenseNet-201
    - MobileNetV3-Large

Grad-CAM explains image regions that influenced the selected
class score. It is not a tumor segmentation method and does
not identify an exact tumor boundary.
"""

import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms


# ==========================================================
# Project and ML paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ML_DIR = PROJECT_ROOT / "ml"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))


# ==========================================================
# Model imports
# ==========================================================

from models.backbones import (
    create_efficientnet_b0,
    create_resnet18,
    create_densenet201,
    create_mobilenet_v3_large,
)

from models.feature_fusion import FusionHead

from models.model_config import (
    CLASS_NAMES,
    FUSION_CHECKPOINT,
    NORMALIZATION_MEAN,
    NORMALIZATION_STD,
)


# ==========================================================
# Configuration
# ==========================================================

IMAGE_SIZE = 224

BACKBONE_ORDER = [
    "efficientnet_b0",
    "resnet18",
    "densenet201",
    "mobilenet_v3_large",
]

FUSION_CHECKPOINT_PATH = PROJECT_ROOT / FUSION_CHECKPOINT


# ==========================================================
# Fusion Grad-CAM
# ==========================================================

class FusionGradCAM:
    """
    Grad-CAM for MedExplain AI's feature-level fusion model.

    The four backbone feature vectors are concatenated and
    passed through the trained fusion head.

    The Grad-CAM target is the selected class logit from the
    fusion head, not an individual backbone prediction.
    """

    def __init__(
        self,
        checkpoint_path: str | Path = FUSION_CHECKPOINT_PATH,
    ) -> None:

        self.device = torch.device("cpu")

        self.activations: dict[str, torch.Tensor] = {}

        print("Loading model for Grad-CAM...")

        # --------------------------------------------------
        # Resolve checkpoint path
        # --------------------------------------------------

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.is_absolute():
            checkpoint_path = PROJECT_ROOT / checkpoint_path

        checkpoint_path = checkpoint_path.resolve()

        print(f"Checkpoint: {checkpoint_path}")

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Fusion checkpoint not found: {checkpoint_path}"
            )

        # --------------------------------------------------
        # Load checkpoint
        # --------------------------------------------------

        checkpoint = torch.load(
            checkpoint_path,
            map_location=self.device,
            weights_only=False,
        )

        # --------------------------------------------------
        # Create backbone architectures
        # --------------------------------------------------

        self.backbones = {
            "efficientnet_b0": create_efficientnet_b0(),
            "resnet18": create_resnet18(),
            "densenet201": create_densenet201(),
            "mobilenet_v3_large": create_mobilenet_v3_large(),
        }

        # --------------------------------------------------
        # Load trained backbone weights
        # --------------------------------------------------

        backbone_states = checkpoint["backbone_state_dicts"]

        for name, model in self.backbones.items():

            model.load_state_dict(
                backbone_states[name]
            )

            model.to(self.device)
            model.eval()

        # --------------------------------------------------
        # Convert backbones into feature extractors
        # --------------------------------------------------

        self.backbones["efficientnet_b0"].classifier = (
            torch.nn.Identity()
        )

        self.backbones["resnet18"].fc = (
            torch.nn.Identity()
        )

        self.backbones["densenet201"].classifier = (
            torch.nn.Identity()
        )

        self.backbones["mobilenet_v3_large"].classifier = (
            torch.nn.Identity()
        )

        # --------------------------------------------------
        # Create and load fusion head
        # --------------------------------------------------

        self.fusion_head = FusionHead()

        self.fusion_head.load_state_dict(
            checkpoint["fusion_head_state_dict"]
        )

        self.fusion_head.to(self.device)
        self.fusion_head.eval()

        # --------------------------------------------------
        # Preprocessing
        #
        # Must match the backend prediction pipeline:
        # RGB -> Resize 224x224 -> Tensor -> Normalize
        # --------------------------------------------------

        self.transform = transforms.Compose(
            [
                transforms.Resize(
                    (IMAGE_SIZE, IMAGE_SIZE)
                ),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=NORMALIZATION_MEAN,
                    std=NORMALIZATION_STD,
                ),
            ]
        )

        # --------------------------------------------------
        # Register Grad-CAM hooks
        # --------------------------------------------------

        self._register_hooks()

        print("Grad-CAM model loaded successfully.")

    # ======================================================
    # Register hooks
    # ======================================================

    def _register_hooks(self) -> None:
        """
        Register forward hooks on the final spatial feature
        layer of each backbone.
        """

        target_layers = {
            "efficientnet_b0": (
                self.backbones["efficientnet_b0"].features[-1]
            ),
            "resnet18": (
                self.backbones["resnet18"].layer4[-1]
            ),
            "densenet201": (
                self.backbones["densenet201"].features
            ),
            "mobilenet_v3_large": (
                self.backbones["mobilenet_v3_large"].features[-1]
            ),
        }

        for name, layer in target_layers.items():

            layer.register_forward_hook(
                self._forward_hook(name)
            )

    # ======================================================
    # Forward hook
    # ======================================================

    def _forward_hook(self, name: str):
        """
        Save the feature activation used to calculate Grad-CAM.

        A clone is returned to avoid problems with later
        in-place operations in the backbone.
        """

        def hook(module, inputs, output):

            if not isinstance(output, torch.Tensor):
                raise TypeError(
                    f"Expected tensor output from {name}, "
                    f"received {type(output)}."
                )

            activation = output.clone()

            self.activations[name] = activation

            # Gradients are retained for this intermediate tensor.
            if activation.requires_grad:
                activation.retain_grad()

            return activation

        return hook

    # ======================================================
    # Feature extraction
    # ======================================================

    def _extract_features(
        self,
        image: torch.Tensor,
    ) -> torch.Tensor:
        """
        Extract features in the same order used by the
        trained feature-fusion model.
        """

        features = []

        # --------------------------------------------------
        # EfficientNet-B0
        # --------------------------------------------------

        model = self.backbones["efficientnet_b0"]

        output = model.features(image)
        output = model.avgpool(output)
        output = torch.flatten(output, 1)

        features.append(output)

        # --------------------------------------------------
        # ResNet-18
        # --------------------------------------------------

        model = self.backbones["resnet18"]

        output = model.conv1(image)
        output = model.bn1(output)
        output = model.relu(output)
        output = model.maxpool(output)

        output = model.layer1(output)
        output = model.layer2(output)
        output = model.layer3(output)
        output = model.layer4(output)

        output = model.avgpool(output)
        output = torch.flatten(output, 1)

        features.append(output)

        # --------------------------------------------------
        # DenseNet-201
        # --------------------------------------------------

        model = self.backbones["densenet201"]

        output = model.features(image)

        output = F.relu(
            output,
            inplace=False,
        )

        output = F.adaptive_avg_pool2d(
            output,
            (1, 1),
        )

        output = torch.flatten(output, 1)

        features.append(output)

        # --------------------------------------------------
        # MobileNetV3-Large
        # --------------------------------------------------

        model = self.backbones["mobilenet_v3_large"]

        output = model.features(image)
        output = model.avgpool(output)
        output = torch.flatten(output, 1)

        features.append(output)

        # --------------------------------------------------
        # Feature-level fusion input
        # --------------------------------------------------

        return torch.cat(
            features,
            dim=1,
        )

    # ======================================================
    # Resolve target class
    # ======================================================

    def _get_target_index(
        self,
        target_class: str | int | None,
        predicted_index: int,
    ) -> int:
        """
        Select the class whose score will be explained.

        If target_class is omitted, explain the predicted class.
        """

        if target_class is None:
            return predicted_index

        if isinstance(target_class, str):

            if target_class not in CLASS_NAMES:
                raise ValueError(
                    f"Unknown target class: {target_class}. "
                    f"Expected one of: {CLASS_NAMES}"
                )

            return CLASS_NAMES.index(target_class)

        target_index = int(target_class)

        if not 0 <= target_index < len(CLASS_NAMES):
            raise ValueError(
                f"Invalid target class index: {target_index}"
            )

        return target_index

    # ======================================================
    # Generate Grad-CAM explanation
    # ======================================================

    def generate(
        self,
        image_path: str | Path,
        target_class: str | int | None = None,
    ) -> dict[str, Any]:
        """
        Generate Grad-CAM for one MRI image.

        Args:
            image_path:
                Path to the MRI image.

            target_class:
                Optional class name or class index.
                If omitted, explains the predicted class.

        Returns:
            Prediction information, class probabilities,
            individual heatmaps, and combined heatmap.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # --------------------------------------------------
        # Reset stored activations
        # --------------------------------------------------

        self.activations = {}

        # --------------------------------------------------
        # Load and preprocess MRI
        # --------------------------------------------------

        try:
            original_image = Image.open(
                image_path
            ).convert("RGB")

        except Exception as exc:
            raise ValueError(
                f"Unable to read MRI image: {image_path}"
            ) from exc

        image_tensor = self.transform(
            original_image
        ).unsqueeze(0).to(self.device)

        # --------------------------------------------------
        # Forward pass
        #
        # Do not wrap this section in torch.no_grad().
        # Grad-CAM requires gradients from the target score.
        # --------------------------------------------------

        self.fusion_head.zero_grad(set_to_none=True)

        for model in self.backbones.values():
            model.zero_grad(set_to_none=True)

        features = self._extract_features(
            image_tensor
        )

        logits = self.fusion_head(
            features
        )

        probabilities = torch.softmax(
            logits,
            dim=1,
        )

        predicted_index = int(
            torch.argmax(
                probabilities,
                dim=1,
            ).item()
        )

        predicted_class = CLASS_NAMES[predicted_index]

        confidence = float(
            probabilities[0, predicted_index].item()
        )

        # --------------------------------------------------
        # Select target class
        # --------------------------------------------------

        target_index = self._get_target_index(
            target_class=target_class,
            predicted_index=predicted_index,
        )

        selected_target_class = CLASS_NAMES[target_index]

        # --------------------------------------------------
        # Backward pass from selected class logit
        # --------------------------------------------------

        target_score = logits[0, target_index]

        target_score.backward()

        # --------------------------------------------------
        # Generate individual backbone Grad-CAM maps
        # --------------------------------------------------

        heatmaps: dict[str, np.ndarray] = {}

        for name in BACKBONE_ORDER:

            activation = self.activations.get(name)

            if activation is None:
                raise RuntimeError(
                    f"No activation captured for {name}."
                )

            gradient = activation.grad

            if gradient is None:
                raise RuntimeError(
                    f"No gradient captured for {name}."
                )

            heatmaps[name] = self._compute_cam(
                activation=activation,
                gradient=gradient,
            )

        # --------------------------------------------------
        # Combine the individual maps
        # --------------------------------------------------

        combined_heatmap = self._combine_heatmaps(
            heatmaps
        )

        # --------------------------------------------------
        # Return class probabilities
        # --------------------------------------------------

        class_probabilities = {
            CLASS_NAMES[index]: float(
                probabilities[0, index].item()
            )
            for index in range(len(CLASS_NAMES))
        }

        return {
            "image_path": str(image_path),

            "predicted_class": predicted_class,

            "predicted_class_index": predicted_index,

            "target_class": selected_target_class,

            "confidence": confidence,

            "class_probabilities": class_probabilities,

            "heatmaps": heatmaps,

            "combined_heatmap": combined_heatmap,
        }

    # ======================================================
    # Compute individual Grad-CAM
    # ======================================================

    def _compute_cam(
        self,
        activation: torch.Tensor,
        gradient: torch.Tensor,
    ) -> np.ndarray:
        """
        Calculate Grad-CAM from one backbone activation.

        Gradients are globally averaged over spatial dimensions
        to obtain channel weights. The weighted activations are
        summed, passed through ReLU, resized, and normalized.
        """

        if activation.ndim != 4:
            raise ValueError(
                "Expected activation shape [batch, channels, height, width], "
                f"received {tuple(activation.shape)}."
            )

        if gradient.shape != activation.shape:
            raise ValueError(
                "Activation and gradient shapes do not match. "
                f"Activation: {tuple(activation.shape)}, "
                f"gradient: {tuple(gradient.shape)}."
            )

        # --------------------------------------------------
        # Global average pooling of gradients
        # --------------------------------------------------

        weights = gradient.mean(
            dim=(2, 3),
            keepdim=True,
        )

        # --------------------------------------------------
        # Weighted sum of feature maps
        # --------------------------------------------------

        cam = (
            weights * activation
        ).sum(
            dim=1,
            keepdim=True,
        )

        # --------------------------------------------------
        # Keep positive evidence
        # --------------------------------------------------

        cam = F.relu(cam)

        # --------------------------------------------------
        # Resize to model input dimensions
        # --------------------------------------------------

        cam = F.interpolate(
            cam,
            size=(IMAGE_SIZE, IMAGE_SIZE),
            mode="bilinear",
            align_corners=False,
        )

        # --------------------------------------------------
        # Remove batch and channel dimensions
        # --------------------------------------------------

        cam = cam[0, 0]

        # --------------------------------------------------
        # Normalize to [0, 1]
        # --------------------------------------------------

        cam_min = cam.min()
        cam_max = cam.max()

        if float((cam_max - cam_min).detach().cpu()) > 1e-8:

            cam = (
                cam - cam_min
            ) / (
                cam_max - cam_min
            )

        else:
            cam = torch.zeros_like(cam)

        return (
            cam.detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    # ======================================================
    # Combine heatmaps
    # ======================================================

    def _combine_heatmaps(
        self,
        heatmaps: dict[str, np.ndarray],
    ) -> np.ndarray:
        """
        Combine the four backbone heatmaps using an equal-weight
        average, then normalize the combined map.

        This produces a combined attention visualization. It
        should not be interpreted as a tumor segmentation mask.
        """

        heatmap_tensors = []

        for name in BACKBONE_ORDER:

            if name not in heatmaps:
                raise KeyError(
                    f"Missing Grad-CAM heatmap for {name}."
                )

            heatmap = torch.as_tensor(
                heatmaps[name],
                dtype=torch.float32,
            )

            if tuple(heatmap.shape) != (
                IMAGE_SIZE,
                IMAGE_SIZE,
            ):
                raise ValueError(
                    f"Unexpected heatmap size for {name}: "
                    f"{tuple(heatmap.shape)}"
                )

            heatmap_tensors.append(heatmap)

        # --------------------------------------------------
        # Equal-weight average
        # --------------------------------------------------

        combined = torch.stack(
            heatmap_tensors,
            dim=0,
        ).mean(dim=0)

        # --------------------------------------------------
        # Normalize combined map
        # --------------------------------------------------

        combined_min = combined.min()
        combined_max = combined.max()

        if float((combined_max - combined_min).cpu()) > 1e-8:

            combined = (
                combined - combined_min
            ) / (
                combined_max - combined_min
            )

        else:
            combined = torch.zeros_like(combined)

        return (
            combined
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    # ======================================================
    # Standalone test
    # ======================================================

    def test(
        self,
        image_path: str | Path,
    ) -> dict[str, Any]:
        """
        Run Grad-CAM and print the prediction details.
        """

        print("\nTesting MedExplain AI Grad-CAM...")

        result = self.generate(image_path)

        print("\nPrediction:")
        print(f"  Class: {result['predicted_class']}")
        print(
            f"  Confidence: "
            f"{result['confidence'] * 100:.4f}%"
        )

        print("\nClass probabilities:")

        for class_name, probability in (
            result["class_probabilities"].items()
        ):
            print(
                f"  {class_name}: "
                f"{probability * 100:.6f}%"
            )

        print("\nIndividual Grad-CAM heatmaps:")

        for name, heatmap in result["heatmaps"].items():
            print(
                f"  {name}: {heatmap.shape}"
            )

        print("\nCombined Grad-CAM:")
        print(
            f"  Shape: {result['combined_heatmap'].shape}"
        )

        return result


# ==========================================================
# Standalone execution
# ==========================================================

if __name__ == "__main__":

    print("\nTesting MedExplain AI Grad-CAM...")

    test_image = (
        PROJECT_ROOT
        / "ml"
        / "data"
        / "processed"
        / "Testing"
        / "pituitary"
        / "Te-pi_1.png"
    )

    gradcam = FusionGradCAM()

    result = gradcam.test(test_image)

    # ------------------------------------------------------
    # Save combined visualization
    # ------------------------------------------------------

    try:

        from explainability.visualization import (
            save_gradcam_visualization,
        )

        output_directory = (
            PROJECT_ROOT
            / "ml"
            / "results"
            / "figures"
            / "gradcam"
        )

        print("\nSaving combined Grad-CAM visualization...")

        paths = save_gradcam_visualization(
            image_path=test_image,
            heatmap=result["combined_heatmap"],
            predicted_class=result["predicted_class"],
            output_dir=output_directory,
        )

        print("\nCombined Grad-CAM files:")

        print(f"  Original: {paths['original']}")
        print(f"  Heatmap : {paths['heatmap']}")
        print(f"  Overlay : {paths['overlay']}")

        print("\nGrad-CAM visualization completed.")

    except Exception as error:

        print("\nVisualization generation failed:")
        print(error)