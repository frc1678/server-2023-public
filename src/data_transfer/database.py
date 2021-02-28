#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Holds functions for database communication.

All communication with the MongoDB local database go through this file.
"""
import os
from typing import Optional, Union

import pymongo
import yaml

import start_mongod
import utils


# Load collection names
COLLECTION_SCHEMA = utils.read_schema('schema/collection_schema.yml')
COLLECTION_NAMES = [collection for collection in COLLECTION_SCHEMA['collections'].keys()]

# Start mongod and initialize replica set
start_mongod.start_mongod()


def check_collection_name(collection_name: str) -> None:
    """Checks if a collection name exists, prints a warning if it doesn't"""
    if collection_name not in COLLECTION_NAMES:
        utils.log_warning(f'database.py: Unexpected collection name: "{collection_name}"')


class Database:
    """Utility class for the database, performs CRUD functions on local and cloud databases"""

    def __init__(self, connection: str = 'localhost', port: int = start_mongod.PORT) -> None:
        self.connection = connection
        self.port = port
        self.client = pymongo.MongoClient(connection, port)
        production_mode: bool = os.environ.get('SCOUTING_SERVER_ENV') == 'production'
        self.name = utils.TBA_EVENT_KEY if production_mode else f'test{utils.TBA_EVENT_KEY}'
        self.db = self.client[self.name]

    def set_indexes(self) -> None:
        """Adds indexes into competition collections"""
        for collection in COLLECTION_SCHEMA['collections']:
            collection_dict = COLLECTION_SCHEMA['collections'][collection]
            if collection_dict['indexes'] is not None:
                for index in collection_dict['indexes']:
                    self.db[collection].create_index(
                        [(field, pymongo.ASCENDING) for field in index['fields']],
                        unique=index['unique'],
                    )

    def find(self, collection: str, **filters: dict) -> list:
        """Finds documents in 'collection', filtering by 'filters'"""
        check_collection_name(collection)
        return list(self.db[collection].find(filters))

    def get_tba_cache(self, api_url: str) -> Optional[dict]:
        """Gets the TBA Cache of 'api_url'"""
        return self.db.tba_cache.find_one({'api_url': api_url})

    def update_tba_cache(self, data: dict, api_url: str) -> None:
        """Updates one TBA Cache at 'api_url'"""
        self.db.tba_cache.update_one({'api_url': api_url}, {'$set': data}, upsert=True)

    def delete_data(self, collection: str, **filters: dict) -> None:
        """Deletes data in 'collection' according to 'filters'"""
        check_collection_name(collection)
        if 'raw' in collection:
            utils.log_warning(f'Attempted to delete raw data from collection {collection}')
            return
        self.db[collection].delete_many(filters)

    def insert_documents(self, collection: str, data: Union[list, dict]) -> None:
        """Inserts documents from 'data' list in 'collection'"""
        check_collection_name(collection)
        if data != [] and isinstance(data, list):
            self.db[collection].insert_many(data)
        elif data != {} and isinstance(data, dict):
            self.db[collection].insert_one(data)
        else:
            utils.log_warning(
                f'database.py: data for insertion to "{collection}" is not a list or dictionary, or is empty'
            )

    def update_document(
        self,
        collection: str,
        new_data: dict,
        query: dict,
    ) -> None:
        """Updates one document that matches 'query' with 'new_data', uses upsert"""
        check_collection_name(collection)
        if 'raw' in collection:
            utils.log_warning(f'Attempted to modify raw data in collection {collection}')
            return
        self.db[collection].update_one(query, {'$set': new_data}, upsert=True)

    def bulk_write(self, collection: str, actions: list) -> pymongo.results.BulkWriteResult:
        """Bulk write `actions` into `collection` in order of `actions`"""
        check_collection_name(collection)
        if 'raw' in collection:
            utils.log_warning(f'Blocked bulk write operation to raw collection {collection}')
            return
        return self.db[collection].bulk_write(actions)
