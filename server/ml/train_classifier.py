"""Train and evaluate the beginner expense-category classifier."""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / 'datasets' / 'expense_categories.csv'
MODEL_PATH = BASE_DIR / 'models' / 'category_classifier.joblib'


def train():
    data = pd.read_csv(DATASET_PATH)
    train_text, test_text, train_labels, test_labels = train_test_split(
        data['description'].str.lower(), data['category'], test_size=0.25,
        random_state=42, stratify=data['category'],
    )
    model = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), stop_words='english')),
        ('classifier', LogisticRegression(max_iter=1000, random_state=42)),
    ])
    model.fit(train_text, train_labels)
    predictions = model.predict(test_text)
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return {
        'accuracy': accuracy_score(test_labels, predictions),
        'report': classification_report(test_labels, predictions, zero_division=0),
        'confusion_matrix': confusion_matrix(test_labels, predictions).tolist(),
    }


if __name__ == '__main__':
    metrics = train()
    print(f"Model saved to {MODEL_PATH}")
    print(f"Accuracy on this tiny sample dataset: {metrics['accuracy']:.2%}")
    print(metrics['report'])
    print('Confusion matrix:', metrics['confusion_matrix'])
