import re

from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import create_app


class FakeAdmin:
    def command(self, name):
        return {'ok': 1}


class FakeResult:
    def __init__(self, inserted_id=None, deleted_count=0):
        self.inserted_id = inserted_id
        self.deleted_count = deleted_count


def matches(document, query):
    for field, value in query.items():
        actual = document.get(field)
        if isinstance(value, dict):
            if '$regex' in value and not re.search(value['$regex'], actual, re.IGNORECASE):
                return False
            if '$gte' in value and actual < value['$gte']:
                return False
            if '$lte' in value and actual > value['$lte']:
                return False
        elif actual != value:
            return False
    return True


class FakeCursor(list):
    def sort(self, field, direction):
        return FakeCursor(sorted(self, key=lambda item: item[field], reverse=direction == -1))


class FakeCollection:
    def __init__(self, unique_email=False):
        self.documents = []
        self.unique_email = unique_email

    def create_index(self, *args, **kwargs):
        return None

    def find_one(self, query):
        return next((document for document in self.documents if matches(document, query)), None)

    def find(self, query):
        return FakeCursor([document for document in self.documents if matches(document, query)])

    def insert_one(self, document):
        if self.unique_email and self.find_one({'email': document['email']}):
            raise DuplicateKeyError('duplicate email')
        document['_id'] = ObjectId()
        self.documents.append(document)
        return FakeResult(inserted_id=document['_id'])

    def find_one_and_update(self, query, update, **kwargs):
        document = self.find_one(query)
        if document:
            document.update(update['$set'])
        return document

    def delete_one(self, query):
        document = self.find_one(query)
        if document:
            self.documents.remove(document)
            return FakeResult(deleted_count=1)
        return FakeResult(deleted_count=0)


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection(unique_email=True)
        self.transactions = FakeCollection()
        self.budgets = FakeCollection()


class FakeClient:
    def __init__(self, *args, **kwargs):
        self.admin = FakeAdmin()
        self.database = FakeDatabase()

    def __getitem__(self, name):
        return self.database


def make_client():
    app = create_app({
        'TESTING': True,
        'MONGODB_URI': 'mongodb://example.test:27017',
        'MONGO_CLIENT_FACTORY': FakeClient,
        'JWT_SECRET_KEY': 'test-secret-key-that-is-at-least-32-bytes',
    })
    return app.test_client()


def auth_header(client, email):
    client.post('/api/v1/auth/register', json={
        'name': email.split('@')[0], 'email': email, 'password': 'secure-password',
    })
    login = client.post('/api/v1/auth/login', json={'email': email, 'password': 'secure-password'})
    return {'Authorization': f"Bearer {login.get_json()['access_token']}"}


def transaction_payload():
    return {
        'description': 'Weekly groceries',
        'amount': 1250.50,
        'date': '2026-11-12',
        'type': 'expense',
        'category': 'Food',
    }


def test_transaction_crud_and_search_filters():
    client = make_client()
    headers = auth_header(client, 'owner@example.com')

    created = client.post('/api/v1/transactions', json=transaction_payload(), headers=headers)
    transaction_id = created.get_json()['transaction']['id']
    listed = client.get('/api/v1/transactions?search=groceries&category=Food', headers=headers)
    updated = client.put(f'/api/v1/transactions/{transaction_id}', json={'amount': 1300}, headers=headers)
    deleted = client.delete(f'/api/v1/transactions/{transaction_id}', headers=headers)

    assert created.status_code == 201
    assert listed.get_json()['transactions'][0]['description'] == 'Weekly groceries'
    assert updated.get_json()['transaction']['amount'] == 1300.0
    assert deleted.status_code == 204
    assert client.get(f'/api/v1/transactions/{transaction_id}', headers=headers).status_code == 404


def test_transaction_access_is_limited_to_the_authenticated_owner():
    client = make_client()
    owner_headers = auth_header(client, 'owner@example.com')
    other_headers = auth_header(client, 'other@example.com')
    created = client.post('/api/v1/transactions', json=transaction_payload(), headers=owner_headers)
    transaction_id = created.get_json()['transaction']['id']

    assert client.get('/api/v1/transactions', headers=other_headers).get_json()['transactions'] == []
    assert client.get(f'/api/v1/transactions/{transaction_id}', headers=other_headers).status_code == 404
    assert client.put(f'/api/v1/transactions/{transaction_id}', json={'amount': 1}, headers=other_headers).status_code == 404
    assert client.delete(f'/api/v1/transactions/{transaction_id}', headers=other_headers).status_code == 404


def test_transaction_validation_rejects_client_supplied_user_id_and_invalid_data():
    client = make_client()
    headers = auth_header(client, 'owner@example.com')
    invalid = {**transaction_payload(), 'amount': -10, 'user_id': str(ObjectId())}

    response = client.post('/api/v1/transactions', json=invalid, headers=headers)

    assert response.status_code == 400
    assert 'Unsupported fields' in response.get_json()['error']
