"""
MedExplain AI - ML Model Loader

Loads the trained feature-fusion model used by the FastAPI backend.

The trained model consists of:
    - EfficientNet-B0
    - ResNet-18
    - DenseNet-201
    - MobileNetV3-Large
    - Feature Fusion Head

This module only loads the existing trained checkpoint.
It does not train or modify the model.
"""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import torch
import torch.nn as nn


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# model_loader.py
#   -> backend/
#       -> app/
#           -> ml/
#
# parents[3] = project root: medexplain_ai/
PROJECT_ROOT = Path(__file__).resolve().parents[3]

ML_ROOT = PROJECT_ROOT / "ml"

CHECKPOINT_PATH = (
    ML_ROOT
    / "results"
    / "checkpoints"
    / "feature_fusion"
    / "medexplain_fusion_model.pth"
)


# ---------------------------------------------------------------------------
# Make the ML package importable from the backend
# ---------------------------------------------------------------------------

ML_ROOT_STRING = str(ML_ROOT)

if ML_ROOT_STRING not in sys.path:
    sys.path.insert(0, ML_ROOT_STRING)


from models.backbones import create_all_backbones
from models.feature_fusion import FusionHead


class MedExplainModelLoader:
    """
    Loads and manages the trained MedExplain AI fusion model.

    The loader reconstructs the four trained backbone architectures,
    removes their classification heads for feature extraction, and loads
    the trained feature-fusion classifier.
    """

    def __init__(
        self,
        checkpoint_path: Path | str = CHECKPOINT_PATH,
        device: str | None = None,
    ) -> None:

        self.checkpoint_path = Path(checkpoint_path)

        # MedExplain AI currently runs on CPU.
        if device is None:
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "cpu"
            )
        else:
            self.device = torch.device(device)

        self.backbones: dict[str, nn.Module] = {}
        self.fusion_head: nn.Module | None = None

        self.class_names: list[str] = []
        self.class_to_idx: dict[str, int] = {}
        self.feature_dims: dict[str, int] = {}

        self.loaded = False

    # -----------------------------------------------------------------------
    # Checkpoint loading
    # -----------------------------------------------------------------------

    def load(self) -> None:
        """Load all trained model components from the fusion checkpoint."""

        if self.loaded:
            return

        if not self.checkpoint_path.exists():
            raise FileNotFoundError(
                "MedExplain AI fusion checkpoint was not found.\n"
                f"Expected path:\n{self.checkpoint_path}"
            )

        print("Loading MedExplain AI fusion model...")
        print(f"Checkpoint: {self.checkpoint_path}")
        print(f"Device: {self.device}")

        checkpoint: dict[str, Any] = torch.load(
            self.checkpoint_path,
            map_location=self.device,
            weights_only=False,
        )

        # ---------------------------------------------------------------
        # Metadata
        # ---------------------------------------------------------------

        self.class_to_idx = checkpoint.get(
            "class_to_idx",
            {
                "glioma": 0,
                "meningioma": 1,
                "notumor": 2,
                "pituitary": 3,
            },
        )

        self.class_names = [
            class_name
            for class_name, _ in sorted(
                self.class_to_idx.items(),
                key=lambda item: item[1],
            )
        ]

        self.feature_dims = checkpoint.get(
            "feature_dims",
            {
                "efficientnet_b0": 1280,
                "resnet18": 512,
                "densenet201": 1920,
                "mobilenet_v3_large": 960,
            },
        )

        # ---------------------------------------------------------------
        # Reconstruct the four backbone architectures
        # ---------------------------------------------------------------

        backbones = create_all_backbones()

        backbone_state_dicts = self._get_backbone_state_dicts(checkpoint)

        for backbone_name, backbone_model in backbones.items():

            if backbone_name not in backbone_state_dicts:
                raise KeyError(
                    f"Checkpoint does not contain weights for "
                    f"'{backbone_name}'."
                )

            backbone_model.load_state_dict(
                backbone_state_dicts[backbone_name]
            )

            # The trained classification head is not needed during
            # fusion inference. Each backbone is used as a feature extractor.
            self._remove_classifier(
                backbone_name,
                backbone_model,
            )

            backbone_model.to(self.device)
            backbone_model.eval()

            self.backbones[backbone_name] = backbone_model

        # ---------------------------------------------------------------
        # Reconstruct fusion head
        # ---------------------------------------------------------------

        fusion_input_dim = sum(self.feature_dims.values())

        # IMPORTANT:
        # The existing FusionHead already defines Dropout(0.3)
        # internally, so dropout must NOT be passed here.
        self.fusion_head = FusionHead(
            input_dim=fusion_input_dim,
            hidden_dim=512,
            num_classes=len(self.class_names),
        )

        fusion_state_dict = self._get_fusion_state_dict(
            checkpoint
        )

        self.fusion_head.load_state_dict(
            fusion_state_dict
        )

        self.fusion_head.to(self.device)
        self.fusion_head.eval()

        self.loaded = True

        print("MedExplain AI fusion model loaded successfully.")
        print(f"Classes: {self.class_names}")
        print(f"Feature dimensions: {self.feature_dims}")
        print(f"Fusion input dimension: {fusion_input_dim}")

    # -----------------------------------------------------------------------
    # Checkpoint compatibility helpers
    # -----------------------------------------------------------------------

    @staticmethod
    def _get_backbone_state_dicts(
        checkpoint: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Retrieve backbone state dictionaries.

        Supports the current checkpoint format and a few reasonable
        key-name variants.
        """

        possible_keys = (
            "backbone_state_dicts",
            "backbones",
            "backbone_states",
        )

        for key in possible_keys:
            if key in checkpoint:
                return checkpoint[key]

        raise KeyError(
            "Could not find backbone state dictionaries in the "
            "MedExplain fusion checkpoint."
        )

    @staticmethod
    def _get_fusion_state_dict(
        checkpoint: dict[str, Any],
    ) -> dict[str, Any]:
        """Retrieve the trained fusion-head state dictionary."""

        possible_keys = (
            "fusion_head_state_dict",
            "fusion_head",
            "fusion_state_dict",
        )

        for key in possible_keys:
            if key in checkpoint:
                return checkpoint[key]

        raise KeyError(
            "Could not find the fusion-head state dictionary in the "
            "MedExplain fusion checkpoint."
        )

    # -----------------------------------------------------------------------
    # Backbone classifier replacement
    # -----------------------------------------------------------------------

    @staticmethod
    def _remove_classifier(
        backbone_name: str,
        model: nn.Module,
    ) -> None:
        """
        Replace the classification layer with Identity.

        Feature dimensions:
            EfficientNet-B0     -> 1280
            ResNet-18           -> 512
            DenseNet-201        -> 1920
            MobileNetV3-Large   -> 960
        """

        if backbone_name == "efficientnet_b0":

            model.classifier[1] = nn.Identity()

        elif backbone_name == "resnet18":

            model.fc = nn.Identity()

        elif backbone_name == "densenet201":

            model.classifier = nn.Identity()

        elif backbone_name == "mobilenet_v3_large":

            model.classifier[3] = nn.Identity()

        else:

            raise ValueError(
                f"Unsupported backbone: {backbone_name}"
            )

    # -----------------------------------------------------------------------
    # Public accessors
    # -----------------------------------------------------------------------

    def get_backbones(self) -> dict[str, nn.Module]:
        """Return the loaded feature-extraction backbones."""

        if not self.loaded:
            self.load()

        return self.backbones

    def get_fusion_head(self) -> nn.Module:
        """Return the loaded fusion classification head."""

        if not self.loaded:
            self.load()

        if self.fusion_head is None:
            raise RuntimeError(
                "Fusion head has not been loaded."
            )

        return self.fusion_head

    def get_device(self) -> torch.device:
        """Return the device being used for inference."""

        return self.device

    def get_class_names(self) -> list[str]:
        """Return class names in model index order."""

        if not self.loaded:
            self.load()

        return self.class_names

    def get_class_to_idx(self) -> dict[str, int]:
        """Return the class-to-index mapping."""

        if not self.loaded:
            self.load()

        return self.class_to_idx

    def get_feature_dims(self) -> dict[str, int]:
        """Return the feature dimensions of all backbones."""

        if not self.loaded:
            self.load()

        return self.feature_dims


# ---------------------------------------------------------------------------
# Singleton model loader
# ---------------------------------------------------------------------------

_model_loader: MedExplainModelLoader | None = None


def get_model_loader() -> MedExplainModelLoader:
    """
    Return the shared MedExplain AI model loader.

    The model is loaded only once and reused by the FastAPI application.
    """

    global _model_loader

    if _model_loader is None:
        _model_loader = MedExplainModelLoader()
        _model_loader.load()

    return _model_loader