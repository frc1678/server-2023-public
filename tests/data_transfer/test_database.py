"""Tests database.py"""
from pymongo import MongoClient
import yaml

from src.data_transfer import database
from src import utils

CLIENT = MongoClient('localhost', 27017)
TEST_DATABASE_NAME = 'test' + utils.TBA_EVENT_KEY
# Helps execute tests
TEST_DB_HELPER = CLIENT[TEST_DATABASE_NAME]
# The actual class to be tested
TEST_DB_ACTUAL = database.Database()


with open('schema/collection_schema.yml', 'r') as collection_schema:
    collections = yaml.load(collection_schema, yaml.Loader)


def test_schema():
    """Compares the schema load to the one in the db file"""
    assert collections == database.COLLECTION_SCHEMA

def test_check_col_name(capsys):
    """Checks collection name checker"""
    database.check_collection_name(TEST_DATABASE_NAME)
    captured = capsys.readouterr()
    assert (
        captured.err
        == f'WARNING: database.py: Unexpected collection name: "{TEST_DATABASE_NAME}"\n'
    )

class TestDatabase:

    def test_init(self):
        """Tests if the init method properly assigns properties of the db class"""
        assert TEST_DB_ACTUAL.connection == 'localhost'
        assert TEST_DB_ACTUAL.port == 27017
        assert TEST_DB_ACTUAL.db.name == TEST_DATABASE_NAME
        test_db = database.Database(connection='test', port=80)
        assert test_db.connection == 'test'
        assert test_db.port == 80
        assert test_db.db.name == TEST_DATABASE_NAME


    def test_indexes(self):
        """Checks if all indexes are added properly"""
        TEST_DB_ACTUAL.set_indexes()
        for collection in collections['collections']:
            collection_dict = collections['collections'][collection]
            if collection_dict['indexes'] is not None:
                for index in collection_dict['indexes']:
                    for db_index in TEST_DB_HELPER[collection].list_indexes():
                        if db_index == 'name':
                            assert dict(db_index)['name'] == [index + '_1']


    def test_find(self):
        """Tests database find"""
        TEST_DB_HELPER.test.insert_one({'test': 'test'})
        assert TEST_DB_ACTUAL.find('test', **{'test': 'test'}) == [TEST_DB_HELPER.test.find_one({})]


    def test_get_tba_cache(self):
        """Tests tba cache read"""
        TEST_DB_HELPER.tba_cache.insert_one({'api_url': 'test'})
        assert TEST_DB_ACTUAL.get_tba_cache('test') == TEST_DB_HELPER.tba_cache.find_one(
            {'api_url': 'test'}
        )


    def test_update_tba_cache(self):
        """Tests updating the tba cache"""
        TEST_DB_ACTUAL.update_tba_cache({'data': 'a'}, 'test')
        test_cache = TEST_DB_HELPER.tba_cache.find_one({})
        assert test_cache['api_url'] == 'test'
        assert test_cache['data'] == 'a'
        TEST_DB_ACTUAL.update_tba_cache({'data': 'b'}, 'test')
        test_cache = TEST_DB_HELPER.tba_cache.find_one({})
        assert test_cache['api_url'] == 'test'
        assert test_cache['data'] == 'b'


    def test_delete_data(self):
        """Tests deletion of data"""
        TEST_DB_HELPER.test.insert_many([{'test': 'test'}, {'test1': 'test1'}])
        TEST_DB_ACTUAL.delete_data('test', **{'test': 'test'})
        assert TEST_DB_HELPER.test.find_one({})['test1'] == 'test1'


    def test_insert_documents(self):
        """Tests insertion of documents"""
        TEST_DB_ACTUAL.insert_documents('test', [{'test': 'a'}])
        assert TEST_DB_HELPER.test.find_one({})['test'] == 'a'
        TEST_DB_ACTUAL.insert_documents('test', {'test_2': 'b'})
        assert TEST_DB_HELPER.test.find_one({'test_2': 'b'})


    def test_update_document(self):
        """Tests updating of documents"""
        TEST_DB_HELPER.test.insert_one({'test': 'a'})
        TEST_DB_ACTUAL.update_document('test', {'test_1': 'b'}, {'test': 'a'})
        test_cache = TEST_DB_HELPER.test.find_one({})
        assert test_cache['test'] == 'a'
        assert test_cache['test_1'] == 'b'
        TEST_DB_ACTUAL.update_document('test', {'test_2': 'c'}, {'test_2': 'a'})
        assert TEST_DB_HELPER.test.find_one({'test_2': 'c'})['test_2'] == 'c'
