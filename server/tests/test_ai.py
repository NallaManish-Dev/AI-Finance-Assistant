from bson import ObjectId

from app.services import ai


class Transactions:
    def find(self, query): return []


class Database:
    transactions = Transactions()


def test_forecast_explains_when_history_is_insufficient(monkeypatch):
    monkeypatch.setattr(ai, 'get_database', lambda: Database())

    result = ai.forecast(ObjectId())

    assert result['status'] == 'insufficient_data'


def test_chat_answers_from_authenticated_users_summary(monkeypatch):
    monkeypatch.setattr(ai, 'summary', lambda user_id: {'expenses': 450, 'income': 1000, 'budget_remaining': 550, 'month': '2026-11'})

    result = ai.chat(ObjectId(), 'How much did I spend this month?')

    assert result['answer'] == 'You spent ₹450.00 this month.'
