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