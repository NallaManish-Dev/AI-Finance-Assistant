from app import create_app
from app.services.database import initialize_database, verify_database_read_write


class FakeAdmin:
    def __init__(self):
        self.commands = []

    def command(self, name):
        self.commands.append(name)
        return {'ok': 1}


class FakeResult:
    inserted_id = 'temporary-document-id'


class FakeCollection:
    def __init__(self):
        self.indexes = []
        self.documents = {}

    def create_index(self, keys, **options):
        self.indexes.append((keys, options))

    def insert_one(self, document):
        self.documents[FakeResult.inserted_id] = document
        return FakeResult()

    def find_one(self, query):
        return self.documents.get(query['_id'])

    def delete_one(self, query):
        self.documents.pop(query['_id'], None)


class FakeDatabase:
    def __init__(self):
        self.users = FakeCollection()
        self.transactions = FakeCollection()
        self.budgets = FakeCollection()


class FakeClient:
    def __init__(self, uri, **kwargs):
        self.uri = uri
        self.kwargs = kwargs
        self.admin = FakeAdmin()
        self.database = FakeDatabase()

    def __getitem__(self, name):
        return self.database


def make_app():
    return create_app(
        {
            'TESTING': True,
            'MONGODB_URI': 'mongodb://example.test:27017',
            'MONGO_CLIENT_FACTORY': FakeClient,
        }
    )


def test_database_setup_pings_server_and_creates_required_indexes():
    app = make_app()

    database = initialize_database(app)

    assert app.extensions['mongo_client'].admin.commands == ['ping']
    assert database.users.indexes == [
        ('email', {'unique': True, 'name': 'users_email_unique'})
    ]
    assert database.transactions.indexes[0][1]['name'] == 'transactions_user_id_date'
    assert database.budgets.indexes[0][1] == {
        'unique': True,
        'name': 'budgets_user_id_month_unique',
    }


def test_database_verification_inserts_reads_and_removes_temporary_document():
    app = make_app()

    verify_database_read_write(app)

    assert app.extensions['mongo_db'].users.documents == {}
