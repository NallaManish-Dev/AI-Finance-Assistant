from flask import Blueprint, g, jsonify, request

from app.routes.auth import require_auth
from app.services.auth import ValidationError
from app.services.dashboard import category_breakdown, monthly_trends, recent_transactions, summary

dashboard_bp = Blueprint('dashboard', __name__)

def error(message): return jsonify({'error': message}), 400

@dashboard_bp.get('/dashboard/summary')
@require_auth
def get_summary():
    try: return jsonify(summary(g.current_user['_id'], request.args.get('month')))
    except ValidationError as exc: return error(str(exc))

@dashboard_bp.get('/analytics/category-breakdown')
@require_auth
def categories():
    try: return jsonify(category_breakdown(g.current_user['_id'], request.args.get('month')))
    except ValidationError as exc: return error(str(exc))

@dashboard_bp.get('/analytics/monthly-trends')
@require_auth
def trends(): return jsonify(monthly_trends(g.current_user['_id']))

@dashboard_bp.get('/dashboard/recent-transactions')
@require_auth
def recent(): return jsonify({'transactions': recent_transactions(g.current_user['_id'])})
