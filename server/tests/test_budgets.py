from bson import ObjectId

from app.services import budgets


class Result:
    def __init__(self, inserted_id=None, deleted_count=0): self.inserted_id, self.deleted_count = inserted_id, deleted_count


def match(document, query):
    for key, value in query.items():
        actual = document.get(key)
        if isinstance(value, dict):
            if '$gte' in value and actual < value['$gte']: return False
            if '$lte' in value and actual > value['$lte']: return False
        elif actual != value: return False
    return True


class Collection:
    def __init__(self): self.documents = []
    def find_one(self, query): return next((item for item in self.documents if match(item, query)), None)
    def find(self, query): return [item for item in self.documents if match(item, query)]
    def insert_one(self, document):
        document['_id'] = ObjectId(); self.documents.append(document); return Result(inserted_id=document['_id'])
    def find_one_and_update(self, query, update, **kwargs):
        item = self.find_one(query)
        if item: item.update(update['$set'])
        return item
    def delete_one(self, query):
        item = self.find_one(query)
        if item: self.documents.remove(item); return Result(deleted_count=1)
        return Result()


class Database:
    def __init__(self): self.budgets, self.transactions = Collection(), Collection()


def test_budget_status_uses_only_the_users_expenses_for_that_month(monkeypatch):
    database, owner, other = Database(), ObjectId(), ObjectId()
    monkeypatch.setattr(budgets, 'get_database', lambda: database)
    created = budgets.create_budget(owner, {'month': '2026-11', 'total_budget': 1000, 'category_limits': {'Food': 400}})
    database.transactions.documents.extend([
        {'user_id': owner, 'type': 'expense', 'date': '2026-11-10', 'amount': 250, 'category': 'Food'},
        {'user_id': owner, 'type': 'income', 'date': '2026-11-11', 'amount': 900, 'category': 'Other'},
        {'user_id': other, 'type': 'expense', 'date': '2026-11-11', 'amount': 700, 'category': 'Food'},
    ])

    status = budgets.budget_status(owner, '2026-11')

    assert created['total_budget'] == 1000.0
    assert status['total_spent'] == 250
    assert status['remaining'] == 750.0
    assert status['percentage_used'] == 25.0
    assert status['category_status']['Food']['remaining'] == 150.0


def test_budget_update_and_delete_are_scoped_to_owner(monkeypatch):
    database, owner, other = Database(), ObjectId(), ObjectId()
    monkeypatch.setattr(budgets, 'get_database', lambda: database)
    budget = budgets.create_budget(owner, {'month': '2026-11', 'total_budget': 1000})

    updated = budgets.update_budget(owner, budget['id'], {'total_budget': 1200})

    assert updated['total_budget'] == 1200.0
    try:
        budgets.delete_budget(other, budget['id'])
        assert False, 'Expected ownership failure'
    except budgets.BudgetNotFoundError:
        pass
