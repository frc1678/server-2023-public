#!/usr/bin/python3.6
"""Holds functions for database communication

All communication with the MongoDB local database go through this file
"""
# External imports
from pymongo import MongoClient
# Internal imports
import utils

DB = MongoClient('localhost', 27017).scouting_system


def overwrite_data_points(data, path, overwrite, competition='current'):
    """Updates data in the 'competitions' collection by overwriting previous data

    data is a string containing data to add to the collection
    path is a string joined by '.' communicating where within the collection the data is added
    overwrite is a string communicating what to overwrite
    competition is the competition code
    """
    if competition == 'current':
        # Obtains the event_code from competition.txt, the file created in setup_competition
        competition = utils.TBA_EVENT_KEY
    # Adds data to the correct path within the competition document
    DB.competitions.update_one({"tba_event_key": competition, path: overwrite},
                               {"$set": {path + '.$': data}})


def append_document(data, path, competition='current'):
    """Appends the 'competitions' collection with new data

    data is a list containing data to add to the collection
    path is a string joined by '.' communicating where within the collection the data is added
    competition is the competition code
    """
    if competition == 'current':
        # Obtains the event_code from competition.txt, the file created in setup_competition
        competition = utils.TBA_EVENT_KEY
    # Adds data to the correct path within the competition document
    DB.competitions.update_one({"tba_event_key": competition}, {'$push': {path: {'$each': data}}})


def select_from_database(query, projection):
    """Selects data from the 'competitions' collection

    query is a dictionary containing the selection filter
    projection is a dictionary containing the data field to collect
    """
    result = []
    cursor = DB.competitions.find(query, projection)
    for i in cursor:
        result.append(i)
    return result


def select_one_from_database(query, projection=None):
    """Selects a single data set from the 'competitions' collection

    query is a dictionary containing the selection filter
    projection is a dictionary containing the data field to collect
    """
    if projection is None:
        query_keys = query.keys()
        for i in query_keys:
            if i == 'raw':
                projection = {'raw': 1}
                break
            if i == 'tba_cache':
                projection = {'tba_cache': 1}
                break
            if i == 'processed':
                projection = {'processed': 1}
                break
    result = DB.competitions.find_one(query, projection)
    new_result = result
    if result is not None:
        result.pop('_id')
        keys = list(result.keys())
        for i in keys:
            if i == 'raw':
                new_result = result.get('raw')
                break
            elif i == 'tba_cache':
                new_result = result.get('tba_cache')
                break
            elif i == 'processed':
                new_result = result.get('processed')
                break
    return new_result


def add_competition(tba_event_key):
    """Adds a new document for the competition into the 'competitions' collection"""
    # Extracts the year from the competition_code
    year = int(tba_event_key[0:4])
    DB.competitions.insert_one({
        'year': year,
        'tba_event_key': tba_event_key,
        'raw': {
            'qr': [],
            'pit': [],
        },
        'tba_cache': [],
        'processed': {
            'replay_outdated_qr': [],
            'unconsolidated_obj_tim': [],
            'consolidated_obj_tim': [],
            'subj_aim': [],
            'calc_team': [],
            'calc_match': [],
            'calc_obj_tim': [],
        },
    })
