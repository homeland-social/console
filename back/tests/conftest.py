import os
import tempfile
import atexit

import pytest

from api import config

DBFD, DBPATH = tempfile.mkstemp()
atexit.register(os.remove, DBPATH)
os.close(DBFD)

# Settings under test.
config.DATABASE['name'] = DBPATH
config.TESTING = True

from api import urls
from api.app import db, app
from api.models import create_tables, drop_tables

@pytest.fixture(autouse=True)
def database():
    create_tables()
    try:
        yield None

    finally:
        drop_tables()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def authenticated():
    with app.test_client() as client:
        with client.session_transaction() as session:
            session['user'] = { 'username': 'testuser', 'email': 'test@test.org' }
        yield client