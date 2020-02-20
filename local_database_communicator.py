#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Holds functions for database communication

All communication with the MongoDB local database go through this file
"""
# External imports
from pymongo import MongoClient
# Internal imports
import utils


def read_dataset(path, competition=utils.TBA_EVENT_KEY, **filter_by):
    """Filters by filter_by if given, or reads entire dataset

    path is a string in dot notation showing which fields the data is under (eg. 'raw.pit').
    competition is the competition code. **filter_by is of the form foo=bar
    and is the key value pair to filter data by
    """
    # If no filter_by is provided, finds all data within the specified path and returns a list
    # of all documents under the field.
    if len(filter_by) == 0:
        result = DB.competitions.find_one({'tba_event_key': competition}, {path: 1, '_id': 0})
    else:
        # Sets up the $eq expression for every filter_by provided
        all_the_filters = []
        for key, value in filter_by.items():
            all_the_filters.append({'$eq': ['$$item.' + key, value]})
        # Uses MongoDB's aggregate function to find documents that match the conditions provided
        # through filter_by
        result = DB.competitions.aggregate([
            {'$match': {'tba_event_key': competition}},
            {
                '$project': {
                    '_id': 0,
                    path: {
                        '$filter': {
                            'input': f'${path}',
                            'as': 'item',
                            'cond': {'$and': all_the_filters}
                        }
                    }
                }
            }
        ])
        # Converts cursor to list
        result = list(result)[0]
    # Remove nesting
    while isinstance(result, dict):
        if not result:
            return []
        result = result[[*result.keys()][0]]
    # Return list of embedded documents
    return result


def select_tba_cache(api_url, competition=utils.TBA_EVENT_KEY):
    """Finds cached tba data from MongoDB.

    If cache exists, returns data. If not, returns None.
    api_url is the url that caches are stored under.
    competition is the competition code.
    """
    cached = DB.competitions.find_one(
        {'tba_event_key': competition}, {f'tba_cache.{api_url}': 1, '_id': 0})['tba_cache']
    return cached


def overwrite_tba_data(data, api_url, competition=utils.TBA_EVENT_KEY):
    """Overwrites data in a tba cache under an api url.

    data is the new data to add. api_url is the url to add it under.
    competition is the competition key.
    """
    # Takes data from tba_communicator and updates it under api_url
    DB.competitions.update_one({'tba_event_key': competition},
                               {'$set': {f'tba_cache.{api_url}': data}})


def remove_data(path, competition=utils.TBA_EVENT_KEY, **filter_by):
    """Removes the document containing the specified filter_bys

     path is a string showing where data is located
     filter_by is a kwarg that show data points in the document
     """
    # Creates dictionary to contain the queries to apply to the specified path
    if filter_by == {}:
        DB.competitions.update_one({'tba_event_key': competition}, {'$set': {path: []}})
        return
    all_the_filters = []
    # Adds every filter_by to the two dictionaries
    for key, value in filter_by.items():
        all_the_filters.append({key: {'$eq': value}})
    # Uses MongoDB update_one() and $pull to remove the document that corresponds to the specified
    # path, competition, and filter_bys
    DB.competitions.update_one({'tba_event_key': competition},
                               {'$pull': {path: {'$and': all_the_filters}}})


def append_or_overwrite(path, data, query=None, competition=utils.TBA_EVENT_KEY):
    """Appends data to dataset if it document doesn't exist. Overwrites if
    it does exist.

    query is the key-value pairs that are used to remove old data during overwrite.
    path is a string in dot notation showing which fields the data is under (eg. 'raw.pit').
    data is the new data to add or overwrite. competition is the competition key.
    """
    # Removes all documents that match the query if it exists.
    # If there is no match, no documents are pulled
    if query is not None:
        DB.competitions.update_one({'tba_event_key': competition}, {'$pull': {path: query}})
    # Add new data
    DB.competitions.update_one({'tba_event_key': competition},
                               {'$addToSet': {path: {'$each': data}}})


def add_competition(db, competition=utils.TBA_EVENT_KEY):
    """Adds a new document for the competition into the 'competitions' collection

    competition is the competition code.
    """
    year = int(competition[0:4])
    db.competitions.insert_one({
        'year': year,
        'tba_event_key': competition,
        'raw': {
            'qr': [],
            'pit': [],
        },
        'tba_cache': {},
        'processed': {
            'replay_outdated_qr': [],
            'unconsolidated_obj_tim': [],
            'calc_obj_tim': [],
            'subj_aim': [],
            'calc_obj_team': [],
            'calc_subj_team': [],
            'calc_match': [],
            'calc_predicted_aim': [],
            'calc_predicted_team': [],
            'calc_tba_team': [],
            'calc_pick_ability_team': [],
        },
    })


DB = MongoClient('localhost', 27017).scouting_system
