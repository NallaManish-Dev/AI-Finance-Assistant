"""Backend-calculated data for the authenticated user's dashboard."""

from datetime import datetime

from app.services.auth import ValidationError
from app.services.budgets import _month
from app.services.database import get_database
from app.services.transactions import CATEGORIES, serialize_transaction


def _selected_month(value=None):
    return _month(value) if value else datetime.now().strftime('%Y-%m')


def _month_transactions(user_id, month):
    return list(get_database().transactions.find({
        'user_id': user_id,
        'date': {'$gte': f'{month}-01', '$lte': f'{month}-31'},
    }))


def summary(user_id, month=None):
    month = _selected_month(month)
    transactions = _month_transactions(user_id, month)
    income = round(sum(item['amount'] for item in transactions if item['type'] == 'income'), 2)
    expenses = round(sum(item['amount'] for item in transactions if item['type'] == 'expense'), 2)
    budget = get_database().budgets.find_one({'user_id': user_id, 'month': month})
    return {
        'month': month,
        'income': income,
        'expenses': expenses,
        'balance': round(income - expenses, 2),
        'budget_remaining': round(budget['total_budget'] - expenses, 2) if budget else None,
        'budget_total': budget['total_budget'] if budget else None,
    }


def category_breakdown(user_id, month=None):
    month = _selected_month(month)
    expenses = [item for item in _month_transactions(user_id, month) if item['type'] == 'expense']
    return {'month': month, 'categories': [
        {'category': category, 'amount': round(sum(item['amount'] for item in expenses if item['category'] == category), 2)}
        for category in CATEGORIES if any(item['category'] == category for item in expenses)
    ]}


def monthly_trends(user_id):
    totals = {}
    for item in get_database().transactions.find({'user_id': user_id}):
        month = item['date'][:7]
        totals.setdefault(month, {'month': month, 'income': 0, 'expenses': 0})
        key = 'income' if item['type'] == 'income' else 'expenses'
        totals[month][key] += item['amount']
    return {'trends': [{**item, 'income': round(item['income'], 2), 'expenses': round(item['expenses'], 2)} for _, item in sorted(totals.items())]}


def recent_transactions(user_id, limit=5):
    cursor = get_database().transactions.find({'user_id': user_id}).sort('date', -1).limit(limit)
    return [serialize_transaction(item) for item in cursor]
