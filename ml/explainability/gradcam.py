"""
MedExplain AI
Grad-CAM explainability for the feature-level fusion model.

Backbones:
    - EfficientNet-B0
    - ResNet-18
    - DenseNet-201
    - MobileNetV3-Large

The Grad-CAM heatmaps explain the final prediction
produced by the feature-level fusion model.
"""

import sys
from pathlib import Path


# ==========================================================
# Project and ML paths
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

ML_DIR = PROJECT_ROOT / "ml"

if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))


import torch
import torch.nn.functional as F

from PIL import Image
from torchvision import transforms


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
# Absolute fusion checkpoint path
# ==========================================================

FUSION_CHECKPOINT_PATH = (
    PROJECT_ROOT / FUSION_CHECKPOINT
)


class FusionGradCAM:
    """
    Grad-CAM for MedExplain AI's feature-level
    fusion architecture.
    """

    def __init__(
        self,
        checkpoint_path=FUSION_CHECKPOINT_PATH,
    ):

        self.device = torch.device("cpu")

        self.activations = {}
        self.activation_gradients = {}

        print(
            "Loading model for Grad-CAM..."
        )

        # ==================================================
        # Load checkpoint
        # ==================================================

        checkpoint_path = Path(checkpoint_path)

        if not checkpoint_path.is_absolute():
            checkpoint_path = PROJECT_ROOT / checkpoint_path

        checkpoint_path = checkpoint_path.resolve()

        print(
            f"Checkpoint: {checkpoint_path}"
        )

        if not checkpoint_path.exists():
            raise FileNotFoundError(
                f"Fusion checkpoint not found: {checkpoint_path}"
            )

        checkpoint = torch.load(
            checkpoint_path,
            map_location=self.device,
            weights_only=False,
        )

        # ==================================================
        # Create backbones
        # ==================================================

        self.backbones = {
            "efficientnet_b0":
                create_efficientnet_b0(),

            "resnet18":
                create_resnet18(),

            "densenet201":
                create_densenet201(),

            "mobilenet_v3_large":
                create_mobilenet_v3_large(),
        }

        # ==================================================
        # Load trained weights
        # ==================================================

        backbone_states = checkpoint[
            "backbone_state_dicts"
        ]

        for name, model in self.backbones.items():

            model.load_state_dict(
                backbone_states[name]
            )

            model.to(self.device)
            model.eval()

        # ==================================================
        # Convert backbones into feature extractors
        # ==================================================

        self.backbones[
            "efficientnet_b0"
        ].classifier = torch.nn.Identity()

        self.backbones[
            "resnet18"
        ].fc = torch.nn.Identity()

        self.backbones[
            "densenet201"
        ].classifier = torch.nn.Identity()

        self.backbones[
            "mobilenet_v3_large"
        ].classifier = torch.nn.Identity()

        # ==================================================
        # Create fusion head
        # ==================================================

        self.fusion_head = FusionHead()

        self.fusion_head.load_state_dict(
            checkpoint[
                "fusion_head_state_dict"
            ]
        )

        self.fusion_head.to(
            self.device
        )

        self.fusion_head.eval()

        # ==================================================
        # Same preprocessing used during training
        # ==================================================

        self.transform = transforms.Compose(
            [
                transforms.ToTensor(),

                transforms.Normalize(
                    mean=NORMALIZATION_MEAN,
                    std=NORMALIZATION_STD,
                ),
            ]
        )

        # ==================================================
        # Register Grad-CAM hooks
        # ==================================================

        self._register_hooks()

        print(
            "Grad-CAM model loaded successfully."
        )

    # ======================================================
    # Register hooks
    # ======================================================

    def _register_hooks(self):

        target_layers = {

            "efficientnet_b0":
                self.backbones[
                    "efficientnet_b0"
                ].features[-1],

            "resnet18":
                self.backbones[
                    "resnet18"
                ].layer4[-1],

            "densenet201":
                self.backbones[
                    "densenet201"
                ].features,

            "mobilenet_v3_large":
                self.backbones[
                    "mobilenet_v3_large"
                ].features[-1],
        }

        for name, layer in (
            target_layers.items()
        ):

            layer.register_forward_hook(
                self._forward_hook(name)
            )

    # ======================================================
    # Forward hook
    # ======================================================

    def _forward_hook(
        self,
        name,
    ):
        """
        Capture the activation tensor.

        The output is cloned before being passed
        forward. This is particularly important for
        DenseNet because its forward method applies
        an in-place ReLU after the features module.
        """

        def hook(
            module,
            inputs,
            output,
        ):

            # ----------------------------------------------
            # Clone the output.
            #
            # This prevents later in-place operations
            # from causing PyTorch autograd conflicts.
            # ----------------------------------------------

            safe_output = output.clone()

            # ----------------------------------------------
            # Store activation
            # ----------------------------------------------

            self.activations[name] = (
                safe_output
            )

            # ----------------------------------------------
            # Retain gradient
            # ----------------------------------------------

            safe_output.retain_grad()

            # ----------------------------------------------
            # Return cloned tensor
            # ----------------------------------------------

            return safe_output

        return hook

    # ======================================================
    # Feature extraction
    # ======================================================

    def _extract_features(
        self,
        image,
    ):

        features = []

        backbone_order = [
            "efficientnet_b0",
            "resnet18",
            "densenet201",
            "mobilenet_v3_large",
        ]

        for name in backbone_order:

            model = self.backbones[name]

            if name == "efficientnet_b0":

                output = model.features(
                    image
                )

                output = model.avgpool(
                    output
                )

                output = torch.flatten(
                    output,
                    1,
                )

            elif name == "resnet18":

                output = model.conv1(image)
                output = model.bn1(output)
                output = model.relu(output)
                output = model.maxpool(output)

                output = model.layer1(output)
                output = model.layer2(output)
                output = model.layer3(output)
                output = model.layer4(output)

                output = model.avgpool(output)

                output = torch.flatten(
                    output,
                    1,
                )

            elif name == "densenet201":

                output = model.features(
                    image
                )

                output = F.relu(
                    output,
                    inplace=False,
                )

                output = F.adaptive_avg_pool2d(
                    output,
                    (1, 1),
                )

                output = torch.flatten(
                    output,
                    1,
                )

            elif name == "mobilenet_v3_large":

                output = model.features(
                    image
                )

                output = model.avgpool(
                    output
                )

                output = torch.flatten(
                    output,
                    1,
                )

            features.append(output)

        return torch.cat(
            features,
            dim=1,
        )

    # ======================================================
    # Generate Grad-CAM explanation
    # ======================================================

    def generate(
        self,
        image_path,
        target_class=None,
    ):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # ----------------------------------------------
        # Reset previous activations
        # ----------------------------------------------

        self.activations = {}

        # ----------------------------------------------
        # Load image
        # ----------------------------------------------

        original_image = Image.open(
            image_path
        ).convert("RGB")

        image_tensor = self.transform(
            original_image
        ).unsqueeze(0).to(
            self.device
        )

        image_tensor.requires_grad_(True)

        # ----------------------------------------------
        # Forward pass
        # ----------------------------------------------

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

        predicted_class = (
            CLASS_NAMES[predicted_index]
        )

        confidence = float(
            probabilities[
                0,
                predicted_index,
            ].item()
        )

        # ----------------------------------------------
        # Target class
        # ----------------------------------------------

        if target_class is None:
            target_index = predicted_index

        elif isinstance(target_class, str):

            if target_class not in CLASS_NAMES:
                raise ValueError(
                    f"Unknown target class: {target_class}"
                )

            target_index = CLASS_NAMES.index(
                target_class
            )

        else:

            target_index = int(
                target_class
            )

            if not (
                0 <= target_index < len(CLASS_NAMES)
            ):
                raise ValueError(
                    f"Invalid target class index: {target_index}"
                )

        # ----------------------------------------------
        # Backward pass
        # ----------------------------------------------

        self.fusion_head.zero_grad()

        for model in self.backbones.values():
            model.zero_grad()

        target_score = logits[
            0,
            target_index,
        ]

        target_score.backward()

        # ----------------------------------------------
        # Generate individual CAMs
        # ----------------------------------------------

        heatmaps = {}

        for name in [
            "efficientnet_b0",
            "resnet18",
            "densenet201",
            "mobilenet_v3_large",
        ]:

            activation = self.activations.get(
                name
            )

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
                activation,
                gradient,
            )

        # ----------------------------------------------
        # Combine heatmaps
        # ----------------------------------------------

        combined_heatmap = (
            self._combine_heatmaps(
                heatmaps
            )
        )

        # ----------------------------------------------
        # Class probabilities
        # ----------------------------------------------

        class_probabilities = {
            CLASS_NAMES[index]:
                float(
                    probabilities[
                        0,
                        index,
                    ].item()
                )
            for index in range(
                len(CLASS_NAMES)
            )
        }

        return {
            "image_path": str(
                image_path
            ),

            "predicted_class":
                predicted_class,

            "predicted_class_index":
                predicted_index,

            "target_class":
                CLASS_NAMES[target_index],

            "confidence":
                confidence,

            "class_probabilities":
                class_probabilities,

            "heatmaps":
                heatmaps,

            "combined_heatmap":
                combined_heatmap,
        }

    # ======================================================
    # Compute individual Grad-CAM
    # ======================================================

    def _compute_cam(
        self,
        activation,
        gradient,
    ):

        # ----------------------------------------------
        # Global average pooling of gradients
        # ----------------------------------------------

        weights = gradient.mean(
            dim=(2, 3),
            keepdim=True,
        )

        # ----------------------------------------------
        # Weighted activation maps
        # ----------------------------------------------

        cam = (
            weights * activation
        ).sum(
            dim=1,
            keepdim=True,
        )

        # ----------------------------------------------
        # ReLU
        # ----------------------------------------------

        cam = F.relu(
            cam
        )

        # ----------------------------------------------
        # Resize to 224 x 224
        # ----------------------------------------------

        cam = F.interpolate(
            cam,
            size=(224, 224),
            mode="bilinear",
            align_corners=False,
        )

        # ----------------------------------------------
        # Remove batch/channel dimensions
        # ----------------------------------------------

        cam = cam[
            0,
            0,
        ]

        # ----------------------------------------------
        # Normalize
        # ----------------------------------------------

        cam_min = cam.min()
        cam_max = cam.max()

        if (
            cam_max - cam_min
        ) > 1e-8:

            cam = (
                cam - cam_min
            ) / (
                cam_max - cam_min
            )

        else:

            cam = torch.zeros_like(
                cam
            )

        return cam.detach().cpu().numpy()

    # ======================================================
    # Combine heatmaps
    # ======================================================

    def _combine_heatmaps(
        self,
        heatmaps,
    ):

        heatmap_tensors = []

        for name in [
            "efficientnet_b0",
            "resnet18",
            "densenet201",
            "mobilenet_v3_large",
        ]:

            heatmap = torch.tensor(
                heatmaps[name],
                dtype=torch.float32,
            )

            heatmap_tensors.append(
                heatmap
            )

        # ----------------------------------------------
        # Equal-weight average
        # ----------------------------------------------

        combined = torch.stack(
            heatmap_tensors,
            dim=0,
        ).mean(
            dim=0
        )

        # ----------------------------------------------
        # Normalize combined map
        # ----------------------------------------------

        combined_min = combined.min()
        combined_max = combined.max()

        if (
            combined_max - combined_min
        ) > 1e-8:

            combined = (
                combined - combined_min
            ) / (
                combined_max - combined_min
            )

        else:

            combined = torch.zeros_like(
                combined
            )

        return combined.numpy()

    # ======================================================
    # Test
    # ======================================================

    def test(
        self,
        image_path,
    ):

        print(
            "\nTesting MedExplain AI Grad-CAM..."
        )

        result = self.generate(
            image_path
        )

        print(
            "\nPrediction:"
        )

        print(
            f"  Class: {result['predicted_class']}"
        )

        print(
            f"  Confidence: "
            f"{result['confidence'] * 100:.2f}%"
        )

        print(
            "\nClass probabilities:"
        )

        for (
            class_name,
            probability,
        ) in result[
            "class_probabilities"
        ].items():

            print(
                f"  {class_name}: "
                f"{probability * 100:.2f}%"
            )

        print(
            "\nIndividual Grad-CAM heatmaps:"
        )

        for (
            name,
            heatmap,
        ) in result[
            "heatmaps"
        ].items():

            print(
                f"  {name}: "
                f"{heatmap.shape}"
            )

        print(
            "\nCombined Grad-CAM:"
        )

        print(
            f"  Shape: "
            f"{result['combined_heatmap'].shape}"
        )

        return result


# ==========================================================
# Standalone test
# ==========================================================

if __name__ == "__main__":

    print(
        "\nTesting MedExplain AI Grad-CAM..."
    )

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

    result = gradcam.test(
        test_image
    )

    # ======================================================
    # Visualization
    # ======================================================

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

        print(
            "\nSaving Grad-CAM visualizations..."
        )

        for (
            backbone_name,
            heatmap,
        ) in result[
            "heatmaps"
        ].items():

            paths = (
                save_gradcam_visualization(
                    image_path=test_image,
                    heatmap=heatmap,
                    backbone_name=backbone_name,
                    output_directory=output_directory,
                    prediction=result[
                        "predicted_class"
                    ],
                    confidence=result[
                        "confidence"
                    ],
                )
            )

            print(
                f"\n{backbone_name}:"
            )

            print(
                f"  Original : "
                f"{paths['original']}"
            )

            print(
                f"  Heatmap  : "
                f"{paths['heatmap']}"
            )

            print(
                f"  Overlay  : "
                f"{paths['overlay']}"
            )

        combined_paths = (
            save_gradcam_visualization(
                image_path=test_image,
                heatmap=result[
                    "combined_heatmap"
                ],
                backbone_name="fusion",
                output_directory=output_directory,
                prediction=result[
                    "predicted_class"
                ],
                confidence=result[
                    "confidence"
                ],
            )
        )

        print(
            "\nFusion Grad-CAM:"
        )

        print(
            f"  Original : "
            f"{combined_paths['original']}"
        )

        print(
            f"  Heatmap  : "
            f"{combined_paths['heatmap']}"
        )

        print(
            f"  Overlay  : "
            f"{combined_paths['overlay']}"
        )

        print(
            "\nGrad-CAM visualization generation "
            "completed successfully."
        )

    except Exception as error:

        print(
            "\nVisualization generation failed:"
        )

        print(
            error
        )