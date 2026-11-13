"""Explainable forecast, insight, and chat helpers using only user data."""

from collections import defaultdict
from datetime import datetime

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error

from app.services.dashboard import category_breakdown, summary
from app.services.database import get_database


def _expense_months(user_id):
    totals = defaultdict(float)
    for item in get_database().transactions.find({'user_id': user_id, 'type': 'expense'}):
        totals[item['date'][:7]] += item['amount']
    return sorted((month, round(amount, 2)) for month, amount in totals.items())


def forecast(user_id):
    months = _expense_months(user_id)
    if len(months) < 3:
        return {'status': 'insufficient_data', 'message': 'At least 3 months of expense history are needed for an estimate.', 'months_available': len(months)}
    values = np.array([amount for _, amount in months])
    positions = np.arange(len(values)).reshape(-1, 1)
    model = LinearRegression().fit(positions, values)
    estimate = float(model.predict([[len(values)]])[0])
    result = {'status': 'ok', 'estimate': round(max(estimate, 0), 2), 'history_months': len(months), 'message': 'This is an estimate based on your recorded past expenses, not a guarantee.'}
    if len(values) >= 4:
        train_x, train_y = positions[:-1], values[:-1]
        evaluation = LinearRegression().fit(train_x, train_y).predict(positions[-1:])
        result['mae'] = round(float(mean_absolute_error(values[-1:], evaluation)), 2)
        result['rmse'] = round(float(root_mean_squared_error(values[-1:], evaluation)), 2)
    return result


def insights(user_id, month=None):
    current = summary(user_id, month)
    result = []
    categories = category_breakdown(user_id, current['month'])['categories']
    if categories:
        highest = max(categories, key=lambda item: item['amount'])
        result.append({'title': 'Highest spending category', 'message': f"{highest['category']} is your highest expense category this month at ₹{highest['amount']:.2f}."})
    if current['budget_total'] is not None:
        used = (current['expenses'] / current['budget_total']) * 100
        if used > 100: result.append({'title': 'Budget exceeded', 'message': f"You are ₹{abs(current['budget_remaining']):.2f} over your monthly budget."})
        elif used >= 80: result.append({'title': 'Budget warning', 'message': f"You have used {used:.0f}% of your monthly budget."})
    if current['expenses'] > current['income']:
        result.append({'title': 'Expenses exceed income', 'message': 'Your recorded expenses are higher than your recorded income this month.'})
    return {'month': current['month'], 'insights': result}


def chat(user_id, message):
    if not isinstance(message, str) or not message.strip(): return {'error': 'A message is required.'}
    text = message.lower()
    current = summary(user_id)
    if 'how much' in text and ('spend' in text or 'expense' in text): answer = f"You spent ₹{current['expenses']:.2f} this month."
    elif ('most' in text or 'highest' in text) and ('category' in text or 'spend' in text):
        categories = category_breakdown(user_id, current['month'])['categories']; answer = f"Your highest category is {max(categories, key=lambda item: item['amount'])['category']}." if categories else 'You have no expense records for this month yet.'
    elif 'budget' in text and ('remaining' in text or 'left' in text): answer = f"Your budget remaining is ₹{current['budget_remaining']:.2f}." if current['budget_remaining'] is not None else 'You have not created a budget for this month yet.'
    else: answer = 'I can answer about this month’s spending, highest category, or remaining budget using your recorded data.'
    return {'answer': answer}
