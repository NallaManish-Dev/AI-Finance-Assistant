from flask import Blueprint, g, jsonify, request

from app.routes.auth import require_auth
from app.services.auth import ValidationError
from app.services.transactions import (
    TransactionNotFoundError,
    create_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
)

transactions_bp = Blueprint('transactions', __name__)


def _error(message, status_code):
    return jsonify({'error': message}), status_code


@transactions_bp.post('/transactions')
@require_auth
def create():
    try:
        transaction = create_transaction(g.current_user['_id'], request.get_json(silent=True))
    except ValidationError as error:
        return _error(str(error), 400)
    return jsonify({'transaction': transaction}), 201


@transactions_bp.get('/transactions')
@require_auth
def list_all():
    try:
        transactions = list_transactions(g.current_user['_id'], request.args)
    except ValidationError as error:
        return _error(str(error), 400)
    return jsonify({'transactions': transactions})


@transactions_bp.get('/transactions/<transaction_id>')
@require_auth
def get_one(transaction_id):
    try:
        transaction = get_transaction(g.current_user['_id'], transaction_id)
    except TransactionNotFoundError as error:
        return _error(str(error), 404)
    return jsonify({'transaction': transaction})


@transactions_bp.put('/transactions/<transaction_id>')
@require_auth
def update(transaction_id):
    try:
        transaction = update_transaction(g.current_user['_id'], transaction_id, request.get_json(silent=True))
    except ValidationError as error:
        return _error(str(error), 400)
    except TransactionNotFoundError as error:
        return _error(str(error), 404)
    return jsonify({'transaction': transaction})


@transactions_bp.delete('/transactions/<transaction_id>')
@require_auth
def delete(transaction_id):
    try:
        delete_transaction(g.current_user['_id'], transaction_id)
    except TransactionNotFoundError as error:
        return _error(str(error), 404)
    return '', 204
