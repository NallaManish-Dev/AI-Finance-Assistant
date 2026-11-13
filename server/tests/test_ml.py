from bson import ObjectId

from app.services import ml


class Predictions:
    def __init__(self): self.documents = []
    def insert_one(self, document): self.documents.append(document)


class Database:
    def __init__(self): self.predictions = Predictions()


def test_prediction_is_saved_separately_from_transaction_category(monkeypatch):
    database = Database()
    monkeypatch.setattr(ml, 'get_database', lambda: database)
    monkeypatch.setattr(ml, 'predict_category', lambda description: {'predicted_category': 'Food', 'confidence': 0.8})

    result = ml.predict_expense_category(ObjectId(), {'description': 'Dinner order'})

    assert result == {'status': 'ok', 'predicted_category': 'Food', 'confidence': 0.8, 'manual_selection_recommended': False}
    assert database.predictions.documents[0]['transaction_id'] is None


def test_missing_model_keeps_manual_category_selection_available(monkeypatch):
    monkeypatch.setattr(ml, 'predict_category', lambda description: None)

    result = ml.predict_expense_category(ObjectId(), {'description': 'Dinner order'})

    assert result['status'] == 'model_unavailable'
