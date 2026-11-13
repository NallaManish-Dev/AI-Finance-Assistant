from flask import Blueprint, g, jsonify, request

from app.routes.auth import require_auth
from app.services.ai import chat, forecast, insights

ai_bp = Blueprint('ai', __name__)

@ai_bp.get('/ml/forecast')
@require_auth
def get_forecast(): return jsonify(forecast(g.current_user['_id']))

@ai_bp.get('/insights')
@require_auth
def get_insights(): return jsonify(insights(g.current_user['_id'], request.args.get('month')))

@ai_bp.post('/chat')
@require_auth
def send_chat():
    result = chat(g.current_user['_id'], (request.get_json(silent=True) or {}).get('message'))
    return (jsonify(result), 400) if 'error' in result else jsonify(result)
