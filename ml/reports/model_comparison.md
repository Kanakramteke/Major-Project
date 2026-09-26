# Model Comparison — MedExplain AI

Test-set performance comparison of the four individual CNN backbones and the feature-level fusion model.

## Test Performance

| Model | Test Accuracy | Weighted Precision | Weighted Recall | Weighted F1 |
|---|---:|---:|---:|---:|
| EfficientNet-B0 | 92.17% | 92.60% | 92.17% | 92.01% |
| ResNet-18 | 81.88% | 82.30% | 81.88% | 81.52% |
| DenseNet-201 | 84.28% | 84.26% | 84.28% | 83.73% |
| MobileNetV3-Large | 87.75% | 87.99% | 87.75% | 87.47% |
| Feature-Level Fusion | 94.00% | 94.41% | 94.00% | 93.87% |


## Dataset

- Task: Four-class brain MRI classification
- Classes: Glioma, Meningioma, No Tumor, Pituitary Tumor
- Test samples: 1,584

## Models

- EfficientNet-B0
- ResNet-18
- DenseNet-201
- MobileNetV3-Large
- Feature-Level Fusion
