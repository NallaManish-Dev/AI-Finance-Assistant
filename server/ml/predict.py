"""Load the saved category model for API predictions."""

from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / 'models' / 'category_classifier.joblib'


def predict_category(description):
    if not MODEL_PATH.exists():
        return None
    model = joblib.load(MODEL_PATH)
    probabilities = model.predict_proba([description.lower()])[0]
    index = probabilities.argmax()
    return {'predicted_category': model.classes_[index], 'confidence': round(float(probabilities[index]), 4)}
