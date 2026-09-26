"""
MedExplain AI - Grad-CAM Visualization Utilities

Utilities for creating and saving:
- Original MRI image
- Grad-CAM heatmap
- Grad-CAM overlay

This module intentionally uses PIL and NumPy only.
It does not use Matplotlib or any GUI backend.
"""

from pathlib import Path

import numpy as np
from PIL import Image


# ---------------------------------------------------------------------------
# Heatmap utilities
# ---------------------------------------------------------------------------

def normalize_heatmap(
    heatmap: np.ndarray,
) -> np.ndarray:
    """
    Normalize a heatmap to the range [0, 1].
    """

    heatmap = np.asarray(
        heatmap,
        dtype=np.float32,
    )

    minimum = float(
        heatmap.min()
    )

    maximum = float(
        heatmap.max()
    )

    if maximum - minimum < 1e-8:
        return np.zeros_like(
            heatmap,
            dtype=np.float32,
        )

    normalized = (
        heatmap - minimum
    ) / (
        maximum - minimum
    )

    return np.clip(
        normalized,
        0.0,
        1.0,
    )


# ---------------------------------------------------------------------------
# Heatmap color generation
# ---------------------------------------------------------------------------

def create_heatmap_image(
    heatmap: np.ndarray,
) -> Image.Image:
    """
    Convert a normalized Grad-CAM heatmap into
    a colored RGB heatmap image.

    A lightweight Jet-style color mapping is implemented
    directly with NumPy so that Matplotlib is not required.
    """

    heatmap = normalize_heatmap(
        heatmap
    )

    # ---------------------------------------------------------------
    # Jet-style color mapping
    # ---------------------------------------------------------------

    red = np.clip(
        1.5 - np.abs(
            4.0 * heatmap - 3.0
        ),
        0.0,
        1.0,
    )

    green = np.clip(
        1.5 - np.abs(
            4.0 * heatmap - 2.0
        ),
        0.0,
        1.0,
    )

    blue = np.clip(
        1.5 - np.abs(
            4.0 * heatmap - 1.0
        ),
        0.0,
        1.0,
    )

    rgb = np.stack(
        [
            red,
            green,
            blue,
        ],
        axis=-1,
    )

    rgb = (
        rgb * 255
    ).astype(
        np.uint8
    )

    return Image.fromarray(
        rgb,
        mode="RGB",
    )


# ---------------------------------------------------------------------------
# Overlay generation
# ---------------------------------------------------------------------------

def create_overlay(
    image: Image.Image,
    heatmap: np.ndarray,
    alpha: float = 0.45,
) -> Image.Image:
    """
    Create a Grad-CAM overlay by blending the
    original MRI image with the colored heatmap.
    """

    image = image.convert(
        "RGB"
    )

    heatmap_image = create_heatmap_image(
        heatmap
    )

    heatmap_image = heatmap_image.resize(
        image.size,
        Image.Resampling.BILINEAR,
    )

    alpha = max(
        0.0,
        min(
            1.0,
            alpha,
        ),
    )

    overlay = Image.blend(
        image,
        heatmap_image,
        alpha,
    )

    return overlay


# ---------------------------------------------------------------------------
# Save Grad-CAM visualization
# ---------------------------------------------------------------------------

def save_gradcam_visualization(
    image_path: str | Path,
    heatmap: np.ndarray,
    predicted_class: str,
    output_dir: str | Path,
) -> dict:
    """
    Save:

    1. Original MRI
    2. Grad-CAM heatmap
    3. Grad-CAM overlay

    Returns absolute paths for all generated files.
    """

    image_path = Path(
        image_path
    )

    output_dir = Path(
        output_dir
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -------------------------------------------------------------------
    # Load original image
    # -------------------------------------------------------------------

    image = Image.open(
        image_path
    ).convert(
        "RGB"
    )

    # -------------------------------------------------------------------
    # Standardize visualization size
    # -------------------------------------------------------------------

    image = image.resize(
        (224, 224),
        Image.Resampling.BILINEAR,
    )

    # -------------------------------------------------------------------
    # Normalize heatmap
    # -------------------------------------------------------------------

    heatmap = normalize_heatmap(
        heatmap
    )

    # -------------------------------------------------------------------
    # File names
    # -------------------------------------------------------------------

    safe_class = (
        predicted_class
        .replace(" ", "_")
        .lower()
    )

    original_path = (
        output_dir
        / f"fusion_{safe_class}_original.png"
    )

    heatmap_path = (
        output_dir
        / f"fusion_{safe_class}_heatmap.png"
    )

    overlay_path = (
        output_dir
        / f"fusion_{safe_class}_overlay.png"
    )

    # -------------------------------------------------------------------
    # Save original image
    # -------------------------------------------------------------------

    image.save(
        original_path,
        format="PNG",
    )

    # -------------------------------------------------------------------
    # Create and save heatmap
    # -------------------------------------------------------------------

    heatmap_image = create_heatmap_image(
        heatmap
    )

    heatmap_image = heatmap_image.resize(
        image.size,
        Image.Resampling.BILINEAR,
    )

    heatmap_image.save(
        heatmap_path,
        format="PNG",
    )

    # -------------------------------------------------------------------
    # Create and save overlay
    # -------------------------------------------------------------------

    overlay = create_overlay(
        image=image,
        heatmap=heatmap,
        alpha=0.45,
    )

    overlay.save(
        overlay_path,
        format="PNG",
    )

    # -------------------------------------------------------------------
    # Return generated file paths
    # -------------------------------------------------------------------

    return {
        "original": str(
            original_path
        ),
        "heatmap": str(
            heatmap_path
        ),
        "overlay": str(
            overlay_path
        ),
    }