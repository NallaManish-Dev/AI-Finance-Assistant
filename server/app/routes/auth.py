from functools import wraps

import jwt
from bson import ObjectId
from flask import Blueprint, current_app, g, jsonify, request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from app.services.auth import (
    AuthenticationError,
    EmailAlreadyExistsError,
    ValidationError,
    authenticate_user,
    create_access_token,
    register_user,
    serialize_user,
)
from app.services.database import get_database

auth_bp = Blueprint('auth', __name__)


def _error(message, status_code):
    return jsonify({'error': message}), status_code


def require_auth(view):
    """Require a valid bearer token and load its user from the database."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        header = request.headers.get('Authorization', '')
        if not header.startswith('Bearer '):
            return _error('Authorization bearer token is required.', 401)

        token = header.removeprefix('Bearer ').strip()
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            user_id = ObjectId(payload['sub'])
        except (ExpiredSignatureError, InvalidTokenError, KeyError, TypeError):
            return _error('Authentication token is invalid or expired.', 401)

        user = get_database().users.find_one({'_id': user_id})
        if not user:
            return _error('Authentication token is invalid.', 401)

        g.current_user = user
        return view(*args, **kwargs)

    return wrapped


@auth_bp.post('/auth/register')
def register():
    try:
        user = register_user(request.get_json(silent=True))
    except ValidationError as error:
        return _error(str(error), 400)
    except EmailAlreadyExistsError as error:
        return _error(str(error), 409)

    return jsonify({'user': user}), 201


@auth_bp.post('/auth/login')
def login():
    try:
        user = authenticate_user(request.get_json(silent=True))
        token = create_access_token(user['_id'], current_app.config)
    except ValidationError as error:
        return _error(str(error), 400)
    except AuthenticationError as error:
        return _error(str(error), 401)
    except RuntimeError as error:
        return _error(str(error), 500)

    return jsonify({'access_token': token, 'user': serialize_user(user)})


@auth_bp.get('/auth/me')
@require_auth
def current_user():
    return jsonify({'user': serialize_user(g.current_user)})


@auth_bp.post('/auth/logout')
@require_auth
def logout():
    """Stateless logout: the client must discard its access token."""
    return jsonify({'message': 'Logged out successfully.'})
