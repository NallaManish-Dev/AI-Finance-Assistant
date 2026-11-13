from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)


@health_bp.get('/health')
def health_check():
    """Return a simple status response without requiring external services."""
    return jsonify({'status': 'ok'}), 200
