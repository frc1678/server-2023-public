#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Sets up the MongoDB document for a competition, should be run before every competition."""

import re

from pymongo import MongoClient

import utils

print('Competition setup started')
COMPETITION_KEY = input('Input the competition code from TBA: ')
# Use a regular expression to determine if competition code is in the correct format
# First capture group: Matches 4 digits
# Second capture group: Matches 1 or more letters
CODE_MATCH = re.fullmatch(r'(?P<year>[0-9]{4})(?P<comp_code>.+)', COMPETITION_KEY)
if CODE_MATCH is None:
    raise ValueError('Competition code is not in the correct format')
# Makes connection with local database through port 27017, the default listening port of MongoDB
CLIENT = MongoClient('localhost', 27017)
# Checks that the competition inputted by the user is not already in the database
if COMPETITION_KEY in CLIENT.list_database_names():
    print(f'WARNING: The competition {COMPETITION_KEY} already exists.')
    if input("Continue anyway? (y or n): ").lower().strip() not in ['y', 'yes']:
        raise Exception('Database already exists')
# Creates the competition.txt file
# Also writes the competition code to it so it can be used in other scripts
with open(utils.create_file_path(utils._TBA_EVENT_KEY_FILE), 'w') as file:
    file.write(COMPETITION_KEY)

from data_transfer import local_database_communicator as ldc

# Creates indexes for the database
ldc.add_competition(CLIENT[COMPETITION_KEY])
CLOUD_DB_PERMISSION = input('Would you like to add this database to the cloud? (y or n): ')
if CLOUD_DB_PERMISSION.lower().strip() in ['y', 'yes']:
    from data_transfer import cloud_database_communicator

    if COMPETITION_KEY in cloud_database_communicator.CLOUD_CLIENT.list_database_names():
        print('WARNING: Database already exists in the cloud, adding anyway')
    cloud_database_communicator.add_competition_cloud(COMPETITION_KEY)
print('Competition setup finished')
