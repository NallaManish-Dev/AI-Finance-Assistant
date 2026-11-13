from datetime import datetime, timezone

from app.services.auth import ValidationError
from app.services.database import get_database
from ml.predict import predict_category


def predict_expense_category(user_id, data):
    if not isinstance(data, dict) or not isinstance(data.get('description'), str) or not data['description'].strip():
        raise ValidationError('A transaction description is required.')
    prediction = predict_category(data['description'].strip())
    if prediction is None:
        return {'status': 'model_unavailable', 'message': 'Category model is not trained yet. Choose a category manually.'}
    get_database().predictions.insert_one({
        'user_id': user_id, 'transaction_id': None, **prediction,
        'created_at': datetime.now(timezone.utc),
    })
    return {'status': 'ok', **prediction, 'manual_selection_recommended': prediction['confidence'] < 0.5}
