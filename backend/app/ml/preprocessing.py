"""
MedExplain AI - MRI Image Preprocessing

Preprocessing used by the FastAPI backend before sending an MRI image
to the trained feature-fusion model.

The preprocessing is consistent with the model inference pipeline:

    1. Load image
    2. Convert to RGB
    3. Resize to 224 x 224
    4. Convert to tensor
    5. Apply ImageNet normalization
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image
import torch
from torchvision import transforms


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

# preprocessing.py
#   -> backend/
#       -> app/
#           -> ml/
#
# parents[3] = project root: medexplain_ai/
PROJECT_ROOT = Path(__file__).resolve().parents[3]


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

IMAGE_SIZE = 224

IMAGENET_MEAN = [
    0.485,
    0.456,
    0.406,
]

IMAGENET_STD = [
    0.229,
    0.224,
    0.225,
]


# ---------------------------------------------------------------------------
# Transformation pipeline
# ---------------------------------------------------------------------------

MRI_TRANSFORM = transforms.Compose(
    [
        transforms.Resize(
            (IMAGE_SIZE, IMAGE_SIZE)
        ),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=IMAGENET_MEAN,
            std=IMAGENET_STD,
        ),
    ]
)


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------

def load_image(
    image_path: str | Path,
) -> Image.Image:
    """
    Load an MRI image from disk and convert it to RGB.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"MRI image was not found: {image_path}"
        )

    try:
        image = Image.open(image_path)
        image = image.convert("RGB")

    except Exception as exc:
        raise ValueError(
            f"Unable to read MRI image: {image_path}"
        ) from exc

    return image


# ---------------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------------

def preprocess_image(
    image_path: str | Path,
) -> torch.Tensor:
    """
    Load and preprocess an MRI image.

    Returns:
        Tensor with shape [1, 3, 224, 224].
    """

    image = load_image(image_path)

    tensor = MRI_TRANSFORM(image)

    tensor = tensor.unsqueeze(0)

    return tensor


# ---------------------------------------------------------------------------
# PIL-image preprocessing
# ---------------------------------------------------------------------------

def preprocess_pil_image(
    image: Image.Image,
) -> torch.Tensor:
    """
    Preprocess an already-loaded PIL image.

    Returns:
        Tensor with shape [1, 3, 224, 224].
    """

    image = image.convert("RGB")

    tensor = MRI_TRANSFORM(image)

    tensor = tensor.unsqueeze(0)

    return tensor


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def validate_preprocessed_tensor(
    tensor: torch.Tensor,
) -> None:
    """
    Validate that the preprocessed tensor has the expected shape.
    """

    expected_shape = (
        1,
        3,
        IMAGE_SIZE,
        IMAGE_SIZE,
    )

    if tuple(tensor.shape) != expected_shape:
        raise ValueError(
            "Unexpected preprocessed MRI tensor shape. "
            f"Expected {expected_shape}, "
            f"received {tuple(tensor.shape)}."
        )


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    print("Testing MedExplain AI MRI preprocessing...")
    print()

    test_image = (
        PROJECT_ROOT
        / "ml"
        / "data"
        / "processed"
        / "Testing"
        / "pituitary"
        / "Te-pi_1.png"
    )

    print(f"Project root: {PROJECT_ROOT}")
    print(f"Test image: {test_image}")
    print()

    tensor = preprocess_image(test_image)

    validate_preprocessed_tensor(tensor)

    print("Preprocessing successful.")
    print(f"Tensor shape: {tuple(tensor.shape)}")
    print(f"Tensor dtype: {tensor.dtype}")
    print(f"Tensor device: {tensor.device}")
    print()
    print("Expected shape: (1, 3, 224, 224)")
    print("MRI preprocessing test PASSED.")