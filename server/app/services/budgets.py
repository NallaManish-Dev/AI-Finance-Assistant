"""Budget validation, ownership-scoped storage, and usage calculations."""

from datetime import datetime

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.services.auth import ValidationError
from app.services.database import get_database
from app.services.transactions import CATEGORIES, _parse_amount


class BudgetNotFoundError(ValueError):
    pass


class BudgetAlreadyExistsError(ValueError):
    pass


def _month(value):
    if not isinstance(value, str):
        raise ValidationError('Month must use YYYY-MM format.')
    try:
        return datetime.strptime(value, '%Y-%m').strftime('%Y-%m')
    except ValueError:
        raise ValidationError('Month must use YYYY-MM format.') from None


def _limits(value):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValidationError('Category limits must be an object.')
    if set(value) - set(CATEGORIES):
        raise ValidationError('Category limits contain an invalid category.')
    limits = {}
    for category, amount in value.items():
        limits[category] = _parse_amount(amount)
    return limits


def validate_budget(data, partial=False):
    allowed = {'month', 'total_budget', 'category_limits'}
    if not isinstance(data, dict):
        raise ValidationError('A JSON request body is required.')
    if set(data) - allowed:
        raise ValidationError('Unsupported budget fields.')
    if not partial and {'month', 'total_budget'} - set(data):
        raise ValidationError('Month and total budget are required.')
    if partial and not data:
        raise ValidationError('At least one budget field is required.')
    clean = {}
    if 'month' in data:
        clean['month'] = _month(data['month'])
    if 'total_budget' in data:
        clean['total_budget'] = _parse_amount(data['total_budget'])
    if 'category_limits' in data:
        clean['category_limits'] = _limits(data['category_limits'])
    return clean


def _id(value):
    if not ObjectId.is_valid(value):
        raise BudgetNotFoundError('Budget not found.')
    return ObjectId(value)


def serialize_budget(budget):
    return {'id': str(budget['_id']), 'month': budget['month'], 'total_budget': budget['total_budget'], 'category_limits': budget.get('category_limits', {})}


def create_budget(user_id, data):
    document = validate_budget(data)
    document['user_id'] = user_id
    try:
        result = get_database().budgets.insert_one(document)
    except DuplicateKeyError as error:
        raise BudgetAlreadyExistsError('A budget already exists for this month.') from error
    document['_id'] = result.inserted_id
    return serialize_budget(document)


def list_budgets(user_id, month=None):
    query = {'user_id': user_id}
    if month:
        query['month'] = _month(month)
    return [serialize_budget(item) for item in get_database().budgets.find(query).sort('month', -1)]


def update_budget(user_id, budget_id, data):
    updated = get_database().budgets.find_one_and_update({'_id': _id(budget_id), 'user_id': user_id}, {'$set': validate_budget(data, partial=True)}, return_document=ReturnDocument.AFTER)
    if not updated:
        raise BudgetNotFoundError('Budget not found.')
    return serialize_budget(updated)


def delete_budget(user_id, budget_id):
    if not get_database().budgets.delete_one({'_id': _id(budget_id), 'user_id': user_id}).deleted_count:
        raise BudgetNotFoundError('Budget not found.')


def budget_status(user_id, month):
    month = _month(month)
    budget = get_database().budgets.find_one({'user_id': user_id, 'month': month})
    if not budget:
        raise BudgetNotFoundError('Budget not found.')
    expenses = list(get_database().transactions.find({'user_id': user_id, 'type': 'expense', 'date': {'$gte': f'{month}-01', '$lte': f'{month}-31'}}))
    spent_by_category = {category: round(sum(item['amount'] for item in expenses if item['category'] == category), 2) for category in CATEGORIES}
    spent = round(sum(item['amount'] for item in expenses), 2)
    total = budget['total_budget']
    category_status = {category: {'limit': limit, 'spent': spent_by_category[category], 'remaining': round(limit - spent_by_category[category], 2), 'percentage_used': round((spent_by_category[category] / limit) * 100, 2) if limit else 0} for category, limit in budget.get('category_limits', {}).items()}
    return {'budget': serialize_budget(budget), 'total_spent': spent, 'remaining': round(total - spent, 2), 'percentage_used': round((spent / total) * 100, 2), 'category_status': category_status}
