from pathlib import Path

from predict import MedExplainFusionModel


TEST_IMAGES = {
    "glioma": Path(
        "ml/data/processed/Testing/glioma/Te-gl_1.png"
    ),
    "meningioma": Path(
        "ml/data/processed/Testing/meningioma/Te-aug-me_1.png"
    ),
    "notumor": Path(
        "ml/data/processed/Testing/notumor/Te-no_1.png"
    ),
    "pituitary": Path(
        "ml/data/processed/Testing/pituitary/Te-pi_1.png"
    ),
}


if __name__ == "__main__":

    print(
        "Testing MedExplain AI fusion model "
        "on one held-out image from each class...\n"
    )

    model = MedExplainFusionModel()

    print()
    print(
        f"{'Actual':<15}"
        f"{'Predicted':<15}"
        f"{'Confidence':<15}"
    )

    print("-" * 45)

    for actual_class, image_path in (
        TEST_IMAGES.items()
    ):

        result = model.predict_image(
            image_path
        )

        print(
            f"{actual_class:<15}"
            f"{result['predicted_class']:<15}"
            f"{result['confidence'] * 100:>6.2f}%"
        )

    print()
    print("Detailed probabilities")
    print("----------------------")

    for actual_class, image_path in (
        TEST_IMAGES.items()
    ):

        result = model.predict_image(
            image_path
        )

        print()
        print(
            f"Actual: {actual_class}"
        )
        print(
            f"Predicted: "
            f"{result['predicted_class']}"
        )
        print(
            f"Confidence: "
            f"{result['confidence'] * 100:.2f}%"
        )

        for class_name, probability in (
            result[
                "class_probabilities"
            ].items()
        ):
            print(
                f"  {class_name:<12}: "
                f"{probability * 100:.2f}%"
            )