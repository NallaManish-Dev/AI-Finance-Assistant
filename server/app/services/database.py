"""MongoDB connection and setup helpers.

The connection is lazy so the basic API can start before a developer has
configured Atlas. Routes added in later steps will use ``get_database``.
"""

from datetime import datetime, timezone
from uuid import uuid4

import click
from flask import current_app
from pymongo import ASCENDING, DESCENDING, MongoClient


def _create_client(app):
    uri = app.config.get('MONGODB_URI')
    if not uri or uri == 'your_mongodb_connection_string':
        raise RuntimeError(
            'MONGODB_URI is not configured. Copy server/.env.example to '
            'server/.env and set your MongoDB Atlas connection string.'
        )

    client_factory = app.config.get('MONGO_CLIENT_FACTORY', MongoClient)
    client = client_factory(
        uri,
        serverSelectionTimeoutMS=app.config['MONGODB_CONNECT_TIMEOUT_MS'],
    )
    client.admin.command('ping')
    return client


def initialize_database(app=None):
    """Connect to MongoDB and create indexes specified by the data design."""
    app = app or current_app

    if 'mongo_db' in app.extensions:
        return app.extensions['mongo_db']

    client = _create_client(app)
    database = client[app.config['MONGODB_DB_NAME']]

    database.users.create_index('email', unique=True, name='users_email_unique')
    database.transactions.create_index(
        [('user_id', ASCENDING), ('date', DESCENDING)],
        name='transactions_user_id_date',
    )
    database.budgets.create_index(
        [('user_id', ASCENDING), ('month', ASCENDING)],
        unique=True,
        name='budgets_user_id_month_unique',
    )

    app.extensions['mongo_client'] = client
    app.extensions['mongo_db'] = database
    return database


def get_database():
    """Return the initialized application database for future route services."""
    return initialize_database()


def verify_database_read_write(app=None):
    """Perform a short-lived, isolated MongoDB read/write verification.

    The temporary document is inserted in the required ``users`` collection
    and always removed afterward.
    """
    database = initialize_database(app)
    verification_email = f'connection-check-{uuid4()}@example.invalid'
    document = {
        'name': 'Connection Check',
        'email': verification_email,
        'password_hash': 'not-a-real-password',
        'created_at': datetime.now(timezone.utc),
    }

    result = database.users.insert_one(document)
    try:
        stored_document = database.users.find_one({'_id': result.inserted_id})
        if stored_document is None:
            raise RuntimeError('MongoDB verification document could not be read.')
    finally:
        database.users.delete_one({'_id': result.inserted_id})


def register_database_commands(app):
    """Register manual database checks without connecting during app startup."""

    @app.cli.command('verify-database')
    def verify_database_command():
        """Connect to Atlas, create indexes, and test an insert/read/delete."""
        verify_database_read_write(app)
        click.echo('MongoDB connection, indexes, and read/write check succeeded.')
