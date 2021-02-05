import os
import sys

from pymongo import MongoClient
import pytest

project_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(project_dir, 'src')
sys.path.insert(0, root)

with open(f'{project_dir}/data/competition.txt') as event_key_file:
    TEST_DATABASE_NAME = 'test' + event_key_file.read().rstrip()

DB = MongoClient(port=1678)[TEST_DATABASE_NAME]


@pytest.fixture(scope='session', autouse=True)
def patch_env():
    PRODUCTION_VARIABLE = 'SCOUTING_SERVER_ENV'
    existing_value = os.environ.get(PRODUCTION_VARIABLE, default=False)
    if PRODUCTION_VARIABLE in os.environ:
        del os.environ[PRODUCTION_VARIABLE]
    assert PRODUCTION_VARIABLE not in os.environ
    yield
    if existing_value:
        os.environ[PRODUCTION_VARIABLE] = existing_value


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    yield
    for collection in DB.list_collection_names():
        DB[collection].delete_many({})


@pytest.fixture(scope='function', autouse=True)
def reset_db():
    for collection in DB.list_collection_names():
        DB[collection].delete_many({})
