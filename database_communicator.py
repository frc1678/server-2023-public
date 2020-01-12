#!/usr/bin/python3.6
"""Holds functions for database communication

All communication with the MongoDB local database go through this file
"""
# External imports
from pymongo import MongoClient
# Internal imports
import utils

DB = MongoClient('localhost', 27017).scouting_system

def append_document(data, path, competition='current'):
    """Appends the 'competitions' collection with new data

    data is a list containing data to add to the collection
    path is a string joined by '.' communicating where within the collection the data is added
    competition is the competition code
    """
    if competition == 'current':
        # Obtains the event_code from competition.txt, the file created in setup_competition
        with open(utils.create_file_path(utils.COMPETITION_CODE_FILE, create_directories=False),
                  'r') as file:
            event_code = file.read()
    else:
        event_code = competition
    # Adds data to the correct path within the competition document
    DB.competitions.update_one({"tba_event_code": event_code}, {'$push': {path: {'$each': data}}})


def add_competition(competition_code):
    """Adds a new document for the competition into the 'competitions' collection
    """
    # Extracts the year from the competition_code
    year = int(competition_code[0:4])
    DB.competitions.insert_one({
        'year': year,
        'tba_event_code': competition_code,
        'raw': {
            'qr_obj': [],
            'qr_subj': [],
            'pit': [],
        },
        'tba_cache': [],
        'processed': {
            'replay_outdated_qr': [],
            'unconsolidated_obj_tim': [],
            'consolidated_obj_tim': [],
            'calc_subj_aim': [],
            'calc_team': [],
            'calc_match': [],
            'calc_obj_tim': [],
        },
    })
