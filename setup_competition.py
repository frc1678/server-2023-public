#!/usr/bin/python3.6
"""Sets up the MongoDB document for a competition.

Run before every competition.
"""
# External imports
from pymongo import MongoClient
import re
# Internal imports
import utils

# Makes a connection with the local database through port 27017, the default listening port of MongoDB
db = MongoClient('localhost', 27017).scouting_system

competition_code = input('Input the competition code from TBA: ')
# Use a regular expression to determine if competition code is in the correct format
# First capture group: Matches 4 digits
# Second capture group: Matches 1 or more letters
code_match = re.fullmatch(r'(?P<year>[0-9]{4})(?P<comp_code>[a-zA-Z]+)', competition_code)
if code_match is None:
    raise Exception('Competition code is not in the correct format')
# Creates the competition.txt file, and writes the competition code to it so it can be used in other scripts.
with open(utils.create_file_path('data/competition.txt'), 'w') as file:
    file.write(competition_code)

# Checks that the competition inputted by the user is not already in the database
if db.competitions.count_documents({'tba_event_code': competition_code}) != 0:
    raise Exception(f'The competition {competition_code} already exists in the database.')

# Extracts the year with capture group
year = int(code_match.group('year'))
# Inserts document into collection
db.competitions.insert_one({
    'year': year,
    'tba_event_code': competition_code,
    'raw': {
        'qr_obj': {},
        'qr_subj': {},
        'pit': {},
    },
    'calculated': {
        'unconsolidated_obj_tim': {},
        'consolidated_obj_tim': {},
        'subj_aim': {},
        'team': {},
        'match': {}, 
    },
})
