"""Authentication business logic, separate from Flask route handlers."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from pymongo.errors import DuplicateKeyError

from app.services.database import get_database


class ValidationError(ValueError):
    """Raised when user-provided authentication data is invalid."""


class AuthenticationError(ValueError):
    """Raised when credentials are not valid."""


class EmailAlreadyExistsError(ValueError):
    """Raised when an email address is already registered."""


def _clean_registration_data(data):
    if not isinstance(data, dict):
        raise ValidationError('A JSON request body is required.')

    name = str(data.get('name', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    password = data.get('password', '')

    if not name:
        raise ValidationError('Name is required.')
    if not email or '@' not in email:
        raise ValidationError('A valid email address is required.')
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError('Password must be at least 8 characters long.')

    return name, email, password


def serialize_user(user):
    """Return only fields that are safe to send to the client."""
    return {
        'id': str(user['_id']),
        'name': user['name'],
        'email': user['email'],
    }


def register_user(data):
    """Create a user while storing only a bcrypt password hash."""
    name, email, password = _clean_registration_data(data)
    database = get_database()

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    document = {
        'name': name,
        'email': email,
        'password_hash': password_hash,
        'created_at': datetime.now(timezone.utc),
    }

    try:
        result = database.users.insert_one(document)
    except DuplicateKeyError as error:
        raise EmailAlreadyExistsError('An account with this email already exists.') from error

    document['_id'] = result.inserted_id
    return serialize_user(document)


def authenticate_user(data):
    """Validate login credentials and return the matching user."""
    if not isinstance(data, dict):
        raise ValidationError('A JSON request body is required.')

    email = str(data.get('email', '')).strip().lower()
    password = data.get('password', '')
    if not email or not isinstance(password, str):
        raise ValidationError('Email and password are required.')

    user = get_database().users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        raise AuthenticationError('Invalid email or password.')

    return user


def create_access_token(user_id, config):
    """Create a signed, expiring JWT access token."""
    secret = config.get('JWT_SECRET_KEY')
    if not secret or secret == 'replace_with_a_long_random_secret':
        raise RuntimeError('JWT_SECRET_KEY must be configured in server/.env.')

    issued_at = datetime.now(timezone.utc)
    payload = {
        'sub': str(user_id),
        'iat': issued_at,
        'exp': issued_at + timedelta(hours=config['JWT_EXPIRATION_HOURS']),
    }
    return jwt.encode(payload, secret, algorithm='HS256')
