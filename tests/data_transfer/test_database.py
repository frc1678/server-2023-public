"""Tests database.py"""
import pymongo
import yaml

from data_transfer import database
from server import Server

CLIENT = pymongo.MongoClient("localhost", 1678)
TEST_DATABASE_NAME = "test" + Server.TBA_EVENT_KEY
# Helps execute tests
TEST_DB_HELPER = CLIENT[TEST_DATABASE_NAME]
# The actual class to be tested
TEST_DB_ACTUAL = database.Database()


with open("schema/collection_schema.yml", "r") as collection_schema:
    collections = yaml.load(collection_schema, yaml.Loader)


def test_schema():
    """Compares the schema load to the one in the db file"""
    assert collections == database.COLLECTION_SCHEMA


def test_check_col_name(caplog):
    """Checks collection name checker"""
    database.check_collection_name(TEST_DATABASE_NAME)
    assert [f'database.py: Unexpected collection name: "{TEST_DATABASE_NAME}"'] == [
        rec.message for rec in caplog.records if rec.levelname == "WARNING"
    ]


class TestDatabase:
    def test_init(self):
        """Tests if the init method properly assigns properties of the db class"""
        assert TEST_DB_ACTUAL.connection == "localhost"
        assert TEST_DB_ACTUAL.port == 1678
        assert TEST_DB_ACTUAL.db.name == TEST_DATABASE_NAME
        test_db = database.Database(connection="test", port=80)
        assert test_db.connection == "test"
        assert test_db.port == 80
        assert test_db.db.name == TEST_DATABASE_NAME
        assert test_db.name == TEST_DATABASE_NAME

    def test_indexes(self):
        """Checks if all indexes are added properly"""
        TEST_DB_ACTUAL.set_indexes()
        for collection in collections["collections"]:
            collection_dict = collections["collections"][collection]
            if collection_dict["indexes"] is not None:
                for index in collection_dict["indexes"]:
                    for db_index in TEST_DB_HELPER[collection].list_indexes():
                        if db_index == "name":
                            db_index_fields = dict(db_index)["name"][0].split("_")
                            for field in index:
                                assert field in db_index_fields

    def test_find(self):
        """Tests database find"""
        TEST_DB_HELPER.test.insert_one({"test": "test"})
        assert TEST_DB_ACTUAL.find("test", {"test": "test"}) == [TEST_DB_HELPER.test.find_one({})]

    def test_get_tba_cache(self):
        """Tests tba cache read"""
        TEST_DB_HELPER.tba_cache.insert_one({"api_url": "test"})
        assert TEST_DB_ACTUAL.get_tba_cache("test") == TEST_DB_HELPER.tba_cache.find_one(
            {"api_url": "test"}
        )

    def test_update_tba_cache(self):
        """Tests updating the tba cache"""
        TEST_DB_ACTUAL.update_tba_cache([{"data": "a"}], "test")
        test_cache = TEST_DB_HELPER.tba_cache.find_one({})
        assert test_cache["api_url"] == "test"
        assert test_cache["data"] == [{"data": "a"}]
        TEST_DB_ACTUAL.update_tba_cache({"data": "b"}, "test")
        test_cache = TEST_DB_HELPER.tba_cache.find_one({})
        assert test_cache["api_url"] == "test"
        assert test_cache["data"] == {"data": "b"}
        TEST_DB_ACTUAL.update_tba_cache({"a": "b"}, "test2", "ETAG")
        test_cache = TEST_DB_HELPER.tba_cache.find_one({"api_url": "test2"})
        del test_cache["_id"]
        assert test_cache == {"data": {"a": "b"}, "etag": "ETAG", "api_url": "test2"}

    def test_delete_data(self):
        """Tests deletion of data"""
        TEST_DB_HELPER.test.insert_many([{"test": "test"}, {"test1": "test1"}])
        TEST_DB_ACTUAL.delete_data("test", {"test": "test"})
        assert TEST_DB_HELPER.test.find_one({})["test1"] == "test1"

    def test_insert_documents(self):
        """Tests insertion of documents"""
        TEST_DB_ACTUAL.insert_documents("test", [{"test": "a"}])
        assert TEST_DB_HELPER.test.find_one({})["test"] == "a"
        TEST_DB_ACTUAL.insert_documents("test", {"test_2": "b"})
        assert TEST_DB_HELPER.test.find_one({"test_2": "b"})

    def test_update_document(self):
        """Tests updating of documents"""
        TEST_DB_HELPER.test.insert_one({"test": "a"})
        TEST_DB_ACTUAL.update_document("test", {"test_1": "b"}, {"test": "a"})
        test_cache = TEST_DB_HELPER.test.find_one({})
        assert test_cache["test"] == "a"
        assert test_cache["test_1"] == "b"
        TEST_DB_ACTUAL.update_document("test", {"test_2": "c"}, {"test_2": "a"})
        assert TEST_DB_HELPER.test.find_one({"test_2": "c"})["test_2"] == "c"

    def test_update_qr_blocklist_status(self):
        """Tests blocklisting of qrs"""
        TEST_DB_HELPER.raw_qr.insert_one(
            {
                "data": "test_qr_string",
                "blocklisted": False,
                "override": {},
                "epoch_time": 1641525570,
                "readable_time": "Thursday, January 6, 2022 7:19:30 PM",
            }
        )
        TEST_DB_ACTUAL.update_qr_blocklist_status({"data": "test_qr_string"})
        test_qr = TEST_DB_HELPER.raw_qr.find_one({})
        assert test_qr["blocklisted"] == True

    def test_update_qr_data_override(self):
        """Tests data override of qrs"""
        TEST_DB_HELPER.raw_qr.insert_one(
            {
                "data": "test_override_qr_string",
                "blocklisted": False,
                "override": {},
                "epoch_time": 1641525570,
                "readable_time": "Sunday, February 5, 2023 4:31:13 PM",
            }
        )
        TEST_DB_ACTUAL.update_qr_data_override(
            {"data": "test_override_qr_string"}, "test", "something"
        )
        test_qr = TEST_DB_HELPER.raw_qr.find_one({})
        assert test_qr["override"] == {"test": "something"}

    def test_bulk_write(self):
        operations = [
            pymongo.InsertOne({"a": 1}),
            pymongo.UpdateOne({"a": 5}, {"$set": {"b": 2}}),
            pymongo.InsertOne({"b": 2}),
        ]
        TEST_DB_ACTUAL.bulk_write("raw_qr", operations)
        result = TEST_DB_ACTUAL.find("raw_qr")
        assert result[0]["a"] == 1
        assert result[1]["b"] == 2
