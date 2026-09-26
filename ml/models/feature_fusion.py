"""
MedExplain AI
Feature-level fusion model.
"""

import torch
import torch.nn as nn

from models.model_config import (
    FUSION_INPUT_DIM,
    FUSION_HIDDEN_DIM,
    NUM_CLASSES,
)


class FusionHead(nn.Module):
    """
    Classification head for the concatenated features
    produced by the four CNN backbones.
    """

    def __init__(
        self,
        input_dim=FUSION_INPUT_DIM,
        hidden_dim=FUSION_HIDDEN_DIM,
        num_classes=NUM_CLASSES,
    ):
        super().__init__()

        self.classifier = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, num_classes),
        )

    def forward(self, features):
        """
        Args:
            features: Tensor of shape [batch_size, 4672]

        Returns:
            logits: Tensor of shape [batch_size, 4]
        """
        return self.classifier(features)


if __name__ == "__main__":
    print("Testing FusionHead...\n")

    model = FusionHead()

    dummy_features = torch.randn(2, FUSION_INPUT_DIM)

    output = model(dummy_features)

    total_params = sum(
        parameter.numel()
        for parameter in model.parameters()
    )

    print(f"Input shape:  {tuple(dummy_features.shape)}")
    print(f"Output shape: {tuple(output.shape)}")
    print(f"Parameters:   {total_params:,}")

    print("\nFusionHead created successfully.")