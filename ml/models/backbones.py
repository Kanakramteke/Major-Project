"""
MedExplain AI
Backbone model definitions for feature-level fusion.
"""

import torch
import torch.nn as nn
from torchvision import models


NUM_CLASSES = 4


def create_efficientnet_b0():
    """
    Create EfficientNet-B0 with the same 4-class
    classifier configuration used during training.
    """

    model = models.efficientnet_b0(weights=None)

    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        NUM_CLASSES,
    )

    return model


def create_resnet18():
    """
    Create ResNet-18 with the same 4-class
    classifier configuration used during training.
    """

    model = models.resnet18(weights=None)

    model.fc = nn.Linear(
        model.fc.in_features,
        NUM_CLASSES,
    )

    return model


def create_densenet201():
    """
    Create DenseNet-201 with the same 4-class
    classifier configuration used during training.
    """

    model = models.densenet201(weights=None)

    model.classifier = nn.Linear(
        model.classifier.in_features,
        NUM_CLASSES,
    )

    return model


def create_mobilenet_v3_large():
    """
    Create MobileNetV3-Large with the same 4-class
    classifier configuration used during training.
    """

    model = models.mobilenet_v3_large(weights=None)

    model.classifier[3] = nn.Linear(
        model.classifier[3].in_features,
        NUM_CLASSES,
    )

    return model


def create_all_backbones():
    """
    Create all four trained backbone architectures.
    """

    return {
        "efficientnet_b0": create_efficientnet_b0(),
        "resnet18": create_resnet18(),
        "densenet201": create_densenet201(),
        "mobilenet_v3_large": create_mobilenet_v3_large(),
    }


if __name__ == "__main__":

    print(
        "Creating MedExplain AI backbone models...\n"
    )

    backbones = create_all_backbones()

    for name, model in backbones.items():

        model.eval()

        total_params = sum(
            parameter.numel()
            for parameter in model.parameters()
        )

        print(f"{name}:")
        print(
            f"  Parameters: {total_params:,}"
        )

    print(
        "\nAll backbone architectures "
        "created successfully."
    )