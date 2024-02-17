import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dir(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    # Create and open a temp file then return its path
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        # Set the database to use the temp file
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

# Create an app object to run the tests without running server
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def run(app):
    return app.test_cli_runner()

# Create a class to reuse for tests related to login
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )
    
    def logout(self):
        return self._client.get('/auth/logout')
    
@pytest.fixture
def auth(client):
    return AuthActions(client)