import collections
import os
import shutil
import subprocess
import time
from unittest import mock

import bson
import pymongo
import pytest
from data_transfer import cloud_db_updater, database
import utils

PORT = 9678


@pytest.fixture(scope='module', autouse=True)
def start_cloud_test_mongod():
    """Runs a mongod instance to replace the functionality of the cloud database

    This removes the need for the tests to connect to the remote database
    """
    db_path = utils.create_file_path('data/cloud_db')
    # Ensure cloud db directory is empty to remove errors
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.mkdir(db_path)
    # Start mongod
    process = subprocess.Popen(['mongod', '--port', str(PORT), '--dbpath', db_path])
    yield
    # Clean up
    process.terminate()
    shutil.rmtree(db_path)


class TestCloudDBUpdater:
    @staticmethod
    def clean_cloud_db(fake_cloud_db: database.Database):
        for collection in fake_cloud_db.db.list_collection_names():
            fake_cloud_db.delete_data(collection, filters={})

    def setup_method(self, method):
        self.start_timestamp = bson.Timestamp(int(time.time()) - 1, 1)
        fake_cloud_db = database.Database(port=PORT)
        self.clean_cloud_db(fake_cloud_db)
        with mock.patch.object(
            cloud_db_updater.CloudDBUpdater, 'get_cloud_db', return_value=fake_cloud_db
        ):
            self.CloudDBUpdater = cloud_db_updater.CloudDBUpdater()

    def test_init(self):
        assert isinstance(self.CloudDBUpdater.cloud_db, database.Database)
        assert isinstance(self.CloudDBUpdater.oplog, pymongo.collection.Collection)
        assert self.CloudDBUpdater.oplog.name == 'oplog.rs'
        assert isinstance(self.CloudDBUpdater.last_timestamp, bson.Timestamp)

    def test_create_bulk_operation_delete(self):
        entry = {
            'ts': 12345,
            'h': -1232132123123,
            'v': 2,
            'op': 'd',
            'ns': 'test.testing',
            'o': {'_id': '1234512345134556'},
        }
        expected = pymongo.DeleteOne({'_id': '1234512345134556'})
        assert self.CloudDBUpdater.create_bulk_operation(entry) == expected

    def test_create_bulk_operation_insert(self):
        entry = {
            'ts': 12345,
            'h': -1232132123123,
            'v': 2,
            'op': 'i',
            'ns': 'test.testing',
            'o': {'_id': '1234512345134556', 't': 42},
        }
        expected = pymongo.InsertOne({'_id': '1234512345134556', 't': 42})
        assert self.CloudDBUpdater.create_bulk_operation(entry) == expected

    def test_create_bulk_operation_update(self):
        entry = {
            'ts': 12345,
            'h': -1232132123123,
            'v': 2,
            'op': 'u',
            'ns': 'test.testing',
            'o': {'$set': {'test': 42}},
            'o2': {'_id': '1234512345134556'},
        }
        expected = pymongo.UpdateOne({'_id': '1234512345134556'}, {'$set': {'test': 42}})
        assert self.CloudDBUpdater.create_bulk_operation(entry) == expected

    def test_entries_since_last(self):
        self.CloudDBUpdater.db.insert_documents('test.testing', ({'a': 1}, {'a': 2}, {'a': 3}))
        self.CloudDBUpdater.db.delete_data('test.testing', a=1)
        self.CloudDBUpdater.db.update_document('test.testing', {'b': 2}, {'a': 2})
        for entry in self.CloudDBUpdater.entries_since_last():
            assert entry['ts'] > self.start_timestamp
            assert entry['op'] in ['d', 'i', 'u']

    def test_create_db_changes(self):
        current_db = self.CloudDBUpdater.db.db.name
        fake_oplog = [
            {'ns': f'{current_db}.test', 'op': 'u', 'o': {'$set': {'v': 1}}, 'o2': {'_id': '1234'}},
            {'ns': f'{current_db}test.test', 'op': 'd', 'o': {'_id': '1234567'}},
            {'ns': f'{current_db}.test', 'op': 'd', 'o': {'_id': '4321'}},
            {'ns': f'{current_db}.test2', 'op': 'i', 'o': {'_id': '43210', 'b': 1}},
        ]
        expected = collections.defaultdict()
        expected['test'] = [
            pymongo.UpdateOne({'_id': '1234'}, {'$set': {'v': 1}}),
            pymongo.DeleteOne({'_id': '4321'}),
        ]
        expected['test2'] = [pymongo.InsertOne({'_id': '43210', 'b': 1})]
        with mock.patch.object(
            self.CloudDBUpdater, 'entries_since_last', return_value=fake_oplog
        ) as _:
            changes = self.CloudDBUpdater.create_db_changes()
        assert changes == expected

    def test_get_connection_string(self):
        with mock.patch(
            'data_transfer.cloud_db_updater.open',
            mock.mock_open(read_data='very_secure_password'),
        ) as mock_open:
            # Make sure that the file contents is inserted and that the correct file path
            # is used.
            result = cloud_db_updater.CloudDBUpdater.get_connection_string()
            assert 'very_secure_password' in result
            assert mock_open.call_args.args[0].endswith('data/api_keys/cloud_password.txt')

    @mock.patch('data_transfer.cloud_db_updater.CloudDBUpdater.update_timestamp')
    def test_write_db_changes(self, mock1):
        changes = collections.defaultdict()
        changes['test'] = [
            pymongo.InsertOne({'_id': '1234', 'v': 2}),
            pymongo.InsertOne({'_id': '4321', 'v': 1}),
            pymongo.UpdateOne({'_id': '1234'}, {'$set': {'v': 1, 'c': 2}}),
        ]
        changes['test2'] = [pymongo.InsertOne({'_id': '43210', 'b': 1})]
        with mock.patch.object(
            self.CloudDBUpdater, 'create_db_changes', return_value=changes
        ) as fake:
            result = self.CloudDBUpdater.write_db_changes()
        assert result['test'].inserted_count == 2
        assert result['test'].modified_count == 1
        assert result['test2'].inserted_count == 1
        assert result['test2'].modified_count == 0
        assert self.CloudDBUpdater.cloud_db.find('test') == [
            {'_id': '1234', 'v': 1, 'c': 2},
            {'_id': '4321', 'v': 1},
        ]
        assert mock1.called

    def test_update_timestamp(self):
        self.CloudDBUpdater.db.insert_documents('test', {'a': 1})
        self.CloudDBUpdater.update_timestamp()
        op = self.CloudDBUpdater.oplog.find_one({'op': 'i', 'o.a': 1})
        assert self.CloudDBUpdater.last_timestamp >= op['ts']
