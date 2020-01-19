#!/usr/bin/python3.6
"""Sets up the MongoDB document for a competition.
Run before every competition.
"""
# External imports
import re
from pymongo import MongoClient
# Internal imports
import utils
import local_database_communicator

# Makes connection with local database through port 27017, the default listening port of MongoDB
DB = MongoClient('localhost', 27017).scouting_system

COMPETITION_KEY = input('Input the competition code from TBA: ')
# Use a regular expression to determine if competition code is in the correct format
# First capture group: Matches 4 digits
# Second capture group: Matches 1 or more letters

CODE_MATCH = re.fullmatch(r'(?P<year>[0-9]{4})(?P<comp_code>[a-zA-Z]+)', COMPETITION_KEY)
if CODE_MATCH is None:
    raise Exception('Competition code is not in the correct format')
# Creates the competition.txt file.
# Also writes the competition code to it so it can be used in other scripts.
utils.save_event_key(COMPETITION_KEY)

# Checks that the competition inputted by the user is not already in the database
if DB.competitions.count_documents({'tba_event_code': COMPETITION_KEY}) != 0:
    raise Exception(f'The competition {COMPETITION_KEY} already exists in the database.')

# Extracts the year with capture group
YEAR = int(CODE_MATCH.group('year'))
# Inserts document into collection
local_database_communicator.add_competition(COMPETITION_KEY)
