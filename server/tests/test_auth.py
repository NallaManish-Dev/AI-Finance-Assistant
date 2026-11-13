from bson import ObjectId
from pymongo.errors import DuplicateKeyError

from app import create_app


class FakeAdmin:
    def command(self, name):
        return {'ok': 1}


class FakeResult:
    def __init__(self, inserted_id):
        self.inserted_id = inserted_id


class FakeUsers:
    def __init__(self):
        self.documents = []

    def create_index(self, *args, **kwargs):
        return None

    def find_one(self, query):
        return next((document for document in self.documents if all(document.get(key) == value for key, value in query.items())), None)

    def insert_one(self, document):
        if self.find_one({'email': document['email']}):
            raise DuplicateKeyError('duplicate email')
        document['_id'] = ObjectId()
        self.documents.append(document)
        return FakeResult(document['_id'])


class FakeCollection:
    def create_index(self, *args, **kwargs):
        return None


class FakeDatabase:
    def __init__(self):
        self.users = FakeUsers()
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


def test_registration_login_and_current_user_flow():
    client = make_client()

    register_response = client.post('/api/v1/auth/register', json={
        'name': 'Sample User',
        'email': 'USER@example.com',
        'password': 'secure-password',
    })
    login_response = client.post('/api/v1/auth/login', json={
        'email': 'user@example.com',
        'password': 'secure-password',
    })

    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert 'password_hash' not in register_response.get_json()['user']

    token = login_response.get_json()['access_token']
    me_response = client.get('/api/v1/auth/me', headers={'Authorization': f'Bearer {token}'})

    assert me_response.status_code == 200
    assert me_response.get_json()['user']['email'] == 'user@example.com'


def test_protected_route_rejects_requests_without_a_valid_token():
    client = make_client()

    response = client.get('/api/v1/auth/me')

    assert response.status_code == 401


def test_duplicate_email_and_invalid_login_are_rejected():
    client = make_client()
    payload = {'name': 'Sample User', 'email': 'user@example.com', 'password': 'secure-password'}
    client.post('/api/v1/auth/register', json=payload)

    duplicate_response = client.post('/api/v1/auth/register', json=payload)
    login_response = client.post('/api/v1/auth/login', json={'email': payload['email'], 'password': 'wrong-password'})

    assert duplicate_response.status_code == 409
    assert login_response.status_code == 401
