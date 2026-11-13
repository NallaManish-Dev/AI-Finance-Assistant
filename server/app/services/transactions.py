"""Transaction validation and database operations."""

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import re

from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument

from app.services.auth import ValidationError
from app.services.database import get_database

CATEGORIES = ('Food', 'Transport', 'Shopping', 'Bills', 'Entertainment', 'Health', 'Education', 'Other')
TRANSACTION_TYPES = ('income', 'expense')
TRANSACTION_FIELDS = {'description', 'amount', 'date', 'type', 'category'}


class TransactionNotFoundError(ValueError):
    """Raised when a transaction is missing or does not belong to the user."""


def serialize_transaction(transaction):
    return {
        'id': str(transaction['_id']),
        'description': transaction['description'],
        'amount': transaction['amount'],
        'date': transaction['date'],
        'type': transaction['type'],
        'category': transaction['category'],
    }


def _parse_amount(value):
    if isinstance(value, bool):
        raise ValidationError('Amount must be a positive number.')
    try:
        amount = Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        raise ValidationError('Amount must be a positive number.') from None
    if amount <= 0:
        raise ValidationError('Amount must be a positive number.')
    return float(amount)


def _parse_date(value):
    if not isinstance(value, str):
        raise ValidationError('Date must use YYYY-MM-DD format.')
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError:
        raise ValidationError('Date must use YYYY-MM-DD format.') from None


def validate_transaction(data, partial=False):
    if not isinstance(data, dict):
        raise ValidationError('A JSON request body is required.')

    unknown_fields = set(data) - TRANSACTION_FIELDS
    if unknown_fields:
        raise ValidationError(f'Unsupported fields: {", ".join(sorted(unknown_fields))}.')
    if partial and not data:
        raise ValidationError('At least one transaction field is required.')

    if not partial:
        missing = TRANSACTION_FIELDS - set(data)
        if missing:
            raise ValidationError(f'Missing required fields: {", ".join(sorted(missing))}.')

    clean = {}
    if 'description' in data:
        description = str(data.get('description', '')).strip()
        if not description:
            raise ValidationError('Description is required.')
        clean['description'] = description
    if 'amount' in data:
        clean['amount'] = _parse_amount(data.get('amount'))
    if 'date' in data:
        clean['date'] = _parse_date(data.get('date'))
    if 'type' in data:
        transaction_type = data.get('type')
        if transaction_type not in TRANSACTION_TYPES:
            raise ValidationError('Type must be income or expense.')
        clean['type'] = transaction_type
    if 'category' in data:
        category = data.get('category')
        if category not in CATEGORIES:
            raise ValidationError(f'Category must be one of: {", ".join(CATEGORIES)}.')
        clean['category'] = category
    return clean


def _transaction_id(transaction_id):
    if not ObjectId.is_valid(transaction_id):
        raise TransactionNotFoundError('Transaction not found.')
    return ObjectId(transaction_id)


def create_transaction(user_id, data):
    document = validate_transaction(data)
    document['user_id'] = user_id
    result = get_database().transactions.insert_one(document)
    document['_id'] = result.inserted_id
    return serialize_transaction(document)


def list_transactions(user_id, filters):
    query = {'user_id': user_id}
    if filters.get('type'):
        if filters['type'] not in TRANSACTION_TYPES:
            raise ValidationError('Type filter must be income or expense.')
        query['type'] = filters['type']
    if filters.get('category'):
        if filters['category'] not in CATEGORIES:
            raise ValidationError('Category filter is invalid.')
        query['category'] = filters['category']
    if filters.get('start_date'):
        query.setdefault('date', {})['$gte'] = _parse_date(filters['start_date'])
    if filters.get('end_date'):
        query.setdefault('date', {})['$lte'] = _parse_date(filters['end_date'])
    if filters.get('search'):
        query['description'] = {'$regex': re.escape(filters['search'].strip()), '$options': 'i'}

    cursor = get_database().transactions.find(query).sort('date', DESCENDING)
    return [serialize_transaction(transaction) for transaction in cursor]


def get_transaction(user_id, transaction_id):
    transaction = get_database().transactions.find_one({'_id': _transaction_id(transaction_id), 'user_id': user_id})
    if not transaction:
        raise TransactionNotFoundError('Transaction not found.')
    return serialize_transaction(transaction)


def update_transaction(user_id, transaction_id, data):
    updates = validate_transaction(data, partial=True)
    transaction = get_database().transactions.find_one_and_update(
        {'_id': _transaction_id(transaction_id), 'user_id': user_id},
        {'$set': updates},
        return_document=ReturnDocument.AFTER,
    )
    if not transaction:
        raise TransactionNotFoundError('Transaction not found.')
    return serialize_transaction(transaction)


def delete_transaction(user_id, transaction_id):
    result = get_database().transactions.delete_one({'_id': _transaction_id(transaction_id), 'user_id': user_id})
    if not result.deleted_count:
        raise TransactionNotFoundError('Transaction not found.')
