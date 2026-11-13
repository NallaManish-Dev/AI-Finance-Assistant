from flask import Blueprint, g, jsonify, request

from app.routes.auth import require_auth
from app.services.auth import ValidationError
from app.services.budgets import BudgetAlreadyExistsError, BudgetNotFoundError, budget_status, create_budget, delete_budget, list_budgets, update_budget

budgets_bp = Blueprint('budgets', __name__)

def error(message, code): return jsonify({'error': message}), code

@budgets_bp.post('/budgets')
@require_auth
def create():
    try: return jsonify({'budget': create_budget(g.current_user['_id'], request.get_json(silent=True))}), 201
    except ValidationError as exc: return error(str(exc), 400)
    except BudgetAlreadyExistsError as exc: return error(str(exc), 409)

@budgets_bp.get('/budgets')
@require_auth
def list_all():
    try: return jsonify({'budgets': list_budgets(g.current_user['_id'], request.args.get('month'))})
    except ValidationError as exc: return error(str(exc), 400)

@budgets_bp.get('/budgets/status')
@require_auth
def status():
    try: return jsonify(budget_status(g.current_user['_id'], request.args.get('month')))
    except ValidationError as exc: return error(str(exc), 400)
    except BudgetNotFoundError as exc: return error(str(exc), 404)

@budgets_bp.put('/budgets/<budget_id>')
@require_auth
def update(budget_id):
    try: return jsonify({'budget': update_budget(g.current_user['_id'], budget_id, request.get_json(silent=True))})
    except ValidationError as exc: return error(str(exc), 400)
    except BudgetNotFoundError as exc: return error(str(exc), 404)

@budgets_bp.delete('/budgets/<budget_id>')
@require_auth
def delete(budget_id):
    try: delete_budget(g.current_user['_id'], budget_id); return '', 204
    except BudgetNotFoundError as exc: return error(str(exc), 404)
