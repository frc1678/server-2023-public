#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Replicates local MongoDB database to cloud MongoDB Atlas database"""
# External imports
import pymongo
# Internal imports
import local_database_communicator
import utils


def update_array(path, change_list):
    """Updates an array of embedded documents. Return 0 on success, 1 if connection was lost."""
    write_operations = []
    # Return blank list if there are no changes at this path
    if not change_list:
        return write_operations
    # Remove documents to be updated
    write_operations.append(pymongo.UpdateOne(
        {'tba_event_key': utils.TBA_EVENT_KEY},
        {'$pull': {path: {'$or': change_list}}}
    ))
    # Select documents to add
    filter_change_list = []
    for change in change_list:
        equals = []
        for key, value in change.items():
            equals.append({'$eq': [f'$$item.{key}', value]})
        filter_change_list.append({'$and': equals})

    to_add = local_database_communicator.DB.competitions.aggregate([
        {'$match': {'tba_event_key': utils.TBA_EVENT_KEY}},
        {'$project':
             {path:
                  {'$filter':
                       {'input': f'${path}', 'as': 'item', 'cond': {'$or': filter_change_list}}
                   }
              }
         }
    ])
    # Aggregate returns a cursor object, so it must be converted to a list. `tba_event_key` is
    # guaranteed to be unique, so there will always one and only one result.
    to_add = list(to_add)[0]
    # Remove `_id` so so the only item is the array nested in the directory structure
    to_add.pop('_id')
    # Remove nesting, making `to_add` only a list of changed documents
    while isinstance(to_add, dict):
        to_add = to_add[[*to_add.keys()][0]]
    write_operations.append(pymongo.UpdateOne(
        {'tba_event_key': utils.TBA_EVENT_KEY}, {'$push': {path: {'$each': to_add}}}
    ))
    return write_operations


def push_changes_to_db(local_change_list, server_restart):
    """Pushes changes to cloud database given the local changes.

    Returns 0 on success, None on failure
    """
    # List of paths that should be directly added (do not point to a document to be updated)
    direct_push = ['raw.qr']
    # Stores PyMongo UpdateOne objects to be written in a bulk write
    write_operations = []
    for section_name, datafield in local_change_list.items():
        for datafield_name, changed_documents in datafield.items():
            path = '.'.join([section_name, datafield_name])
            # Cloud data should be replaced on server restart, so all existing data should be
            # removed so no outdated data remains
            if server_restart:
                write_operations.append(pymongo.UpdateOne({'tba_event_key': utils.TBA_EVENT_KEY},
                                                          {'$set': {path: []}}))
            if path in direct_push:
                write_operations.append(pymongo.UpdateOne(
                    {'tba_event_key': utils.TBA_EVENT_KEY},
                    {'$push': {path: {'$each': changed_documents}}}
                ))
                continue
            # Join list returned by update_array with existing write operations
            write_operations.extend(update_array(path, changed_documents))
    # Write changes to database
    # Ordered must be true because we pull outdated data before pushing new data
    # Throws error on lost connection
    try:
        CLOUD_DB.competitions.bulk_write(write_operations, ordered=True)
    except pymongo.errors.AutoReconnect:
        utils.log_warning('Cloud Database Write Timeout.')
        return None
    return 0


def add_competition_cloud(tba_event_key):
    """Adds competition document to cloud database."""
    local_database_communicator.add_competition(CLOUD_DB, tba_event_key)


# Connect to cloud database
with open(utils.create_file_path('data/api_keys/cloud_password.txt')) as file:
    CLOUD_PASSWORD = file.read().rstrip('\n')
DB_ADDRESS = f'mongodb+srv://server:{CLOUD_PASSWORD}@scouting-system-3das1.gcp.mongodb.net/test?retryWrites=true&w=majority'
CLOUD_DB = pymongo.MongoClient(DB_ADDRESS).scouting_system_cloud
# Creates cloud database indexes (if they don't already exist)
CLOUD_DB.competitions.create_indexes([
    pymongo.IndexModel('tba_event_key', unique=True),
    pymongo.IndexModel('year', unique=False)
])
