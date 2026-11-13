from bson import ObjectId

from app.services import dashboard


class Cursor(list):
    def sort(self, field, direction): return Cursor(sorted(self, key=lambda item: item[field], reverse=True))
    def limit(self, count): return Cursor(self[:count])

class Collection:
    def __init__(self, documents): self.documents = documents
    def find(self, query):
        result = []
        for item in self.documents:
            if item.get('user_id') != query.get('user_id'): continue
            if 'date' in query and not (query['date']['$gte'] <= item['date'] <= query['date']['$lte']): continue
            result.append(item)
        return Cursor(result)
    def find_one(self, query): return next((item for item in self.documents if all(item.get(key) == value for key, value in query.items())), None)

class Database:
    def __init__(self, transactions, budgets): self.transactions, self.budgets = Collection(transactions), Collection(budgets)

def test_dashboard_uses_only_current_users_data(monkeypatch):
    owner, other = ObjectId(), ObjectId()
    database = Database([
        {'_id': ObjectId(), 'user_id': owner, 'description': 'Salary', 'amount': 1000, 'date': '2026-11-01', 'type': 'income', 'category': 'Other'},
        {'_id': ObjectId(), 'user_id': owner, 'description': 'Groceries', 'amount': 250, 'date': '2026-11-02', 'type': 'expense', 'category': 'Food'},
        {'_id': ObjectId(), 'user_id': other, 'description': 'Other data', 'amount': 999, 'date': '2026-11-02', 'type': 'expense', 'category': 'Food'},
    ], [{'_id': ObjectId(), 'user_id': owner, 'month': '2026-11', 'total_budget': 800}])
    monkeypatch.setattr(dashboard, 'get_database', lambda: database)

    data = dashboard.summary(owner, '2026-11')
    categories = dashboard.category_breakdown(owner, '2026-11')

    assert data == {'month': '2026-11', 'income': 1000, 'expenses': 250, 'balance': 750, 'budget_remaining': 550, 'budget_total': 800}
    assert categories['categories'] == [{'category': 'Food', 'amount': 250}]
