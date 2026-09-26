"""
MedExplain AI
Model configuration shared across inference and explainability modules.
"""

# ---------------------------------------------------------
# Classification
# ---------------------------------------------------------

CLASS_NAMES = [
    "glioma",
    "meningioma",
    "notumor",
    "pituitary",
]

CLASS_TO_INDEX = {
    "glioma": 0,
    "meningioma": 1,
    "notumor": 2,
    "pituitary": 3,
}

INDEX_TO_CLASS = {
    index: name
    for name, index in CLASS_TO_INDEX.items()
}


# ---------------------------------------------------------
# Image preprocessing
# ---------------------------------------------------------

IMAGE_SIZE = (224, 224)

NORMALIZATION_MEAN = [
    0.485,
    0.456,
    0.406,
]

NORMALIZATION_STD = [
    0.229,
    0.224,
    0.225,
]


# ---------------------------------------------------------
# Feature-level fusion
# ---------------------------------------------------------

BACKBONE_FEATURE_DIMENSIONS = {
    "efficientnet_b0": 1280,
    "resnet18": 512,
    "densenet201": 1920,
    "mobilenet_v3_large": 960,
}

FUSION_INPUT_DIM = sum(
    BACKBONE_FEATURE_DIMENSIONS.values()
)

FUSION_HIDDEN_DIM = 512

NUM_CLASSES = len(CLASS_NAMES)


# ---------------------------------------------------------
# Model information
# ---------------------------------------------------------

MODEL_NAME = "MedExplain AI Feature-Level Fusion"

BACKBONE_NAMES = [
    "efficientnet_b0",
    "resnet18",
    "densenet201",
    "mobilenet_v3_large",
]


# ---------------------------------------------------------
# Checkpoint
# ---------------------------------------------------------

FUSION_CHECKPOINT = (
    "ml/results/checkpoints/"
    "feature_fusion/medexplain_fusion_model.pth"
)



if __name__ == "__main__":
    print("Model configuration loaded successfully.")
    print("Classes:", CLASS_NAMES)
    print("Number of classes:", NUM_CLASSES)
    print("Image size:", IMAGE_SIZE)
    print("Fusion input dimension:", FUSION_INPUT_DIM)
    print("Fusion hidden dimension:", FUSION_HIDDEN_DIM)
    print("Backbone feature dimensions:")
    
    for name, dimension in BACKBONE_FEATURE_DIMENSIONS.items():
        print(f"  {name}: {dimension}")