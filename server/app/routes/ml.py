from flask import Blueprint, g, jsonify, request

from app.routes.auth import require_auth
from app.services.auth import ValidationError
from app.services.ml import predict_expense_category

ml_bp = Blueprint('ml', __name__)

@ml_bp.post('/ml/predict-category')
@require_auth
def predict_category():
    try:
        return jsonify(predict_expense_category(g.current_user['_id'], request.get_json(silent=True)))
    except ValidationError as error:
        return jsonify({'error': str(error)}), 400
