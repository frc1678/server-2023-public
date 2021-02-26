import os
import shutil
import sys
import subprocess
from unittest import mock

from pymongo import MongoClient
import pytest

project_dir = os.path.dirname(os.path.abspath(__file__))
root = os.path.join(project_dir, 'src')
sys.path.insert(0, root)

# Needed to properly mock cloud db
from data_transfer.database import Database

with open(f'{project_dir}/data/competition.txt') as event_key_file:
    TEST_DATABASE_NAME = 'test' + event_key_file.read().rstrip()

DB = MongoClient(port=1678)[TEST_DATABASE_NAME]


def pytest_configure(config):
    config.addinivalue_line("markers", "clouddb: mark that test needs the cloud db to be reset")


def pytest_addoption(parser):
    parser.addoption(
        '--always-reset-cloud',
        action='store_true',
        default=False,
        help='Reset the Cloud DB after every test instead of specific tests. Default False',
    )


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
def start_cloud_test_mongod():
    """Runs a mongod instance to replace the functionality of the cloud database

    This removes the need for the tests to connect to the remote database
    """
    db_path = f'{project_dir}/data/cloud_db'
    # Ensure cloud db directory is empty to remove errors
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.mkdir(db_path)
    # Start mongod
    process = subprocess.Popen(['mongod', '--port', '9678', '--dbpath', db_path])
    yield
    # Clean up
    process.terminate()
    # Wait for process to terminate so CI runs work
    while process.poll() is None:
        pass
    shutil.rmtree(db_path)


@pytest.fixture()
def cloud_db():
    return Database(port=9678)


@pytest.fixture(scope='function', autouse=True)
def mock_cloud_db_and_clean(request, monkeypatch, cloud_db):
    monkeypatch.setattr(
        'data_transfer.cloud_db_updater.CloudDBUpdater.get_cloud_db',
        mock.Mock(return_value=cloud_db),
    )
    # Don't reset if test is missing the `clouddb` mark and `--always-reset-cloud` is not set
    if 'clouddb' in request.keywords or request.config.getoption('--always-reset-cloud'):
        yield
        for collection in cloud_db.db.list_collection_names():
            cloud_db.delete_data(collection)
    else:
        yield


@pytest.fixture(scope='session', autouse=True)
def clear_db():
    yield
    for collection in DB.list_collection_names():
        DB[collection].delete_many({})


@pytest.fixture(scope='function', autouse=True)
def reset_db():
    for collection in DB.list_collection_names():
        DB[collection].delete_many({})
