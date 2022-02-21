#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Adds QR codes to a blocklist in the local database based on match number or blocklists
a specific QR code based on match number and tablet serial number.

If rollback match is selected, all QR codes from matches with the user inputted match number are
blocklisted. If blocklist a specific QR is selected, all QR codes from a specific
tablet serial number, and match number are added to the blocklist.
"""

import re
import sys

from src.data_transfer import database
from src import utils
from server import Server

db = database.Database()

# Takes user input to find which operation to do
ROLLBACK_OR_BLOCKLIST = input('Rollback a match (0) or blocklist specific qrs (1)? (0,1): ')

# If user doesn't enter a valid option, exit
if ROLLBACK_OR_BLOCKLIST not in ['0', '1']:
    print('Please enter a valid number', file=sys.stderr)
    sys.exit()


print('WARNING: data from matching QR codes will be blocklisted or deleted')

# User input for match to delete
INVALID_MATCH = input('Enter the match to blocklist: ')

# If the user inputted match number is not a number, exit
if not INVALID_MATCH.isnumeric():
    print('Please enter a number')
    sys.exit()

# Opens the schema document, to be used in regexes
SCHEMA = utils.read_schema('schema/match_collection_qr_schema.yml')

# Stores all of the elements of the regex to be joined to a string later
PATTERN_ELEMENTS = [
    '.*',  # Matches any character
    SCHEMA['generic_data']['match_number'][0] + INVALID_MATCH,  # Matches the match number
    '\\' + SCHEMA['generic_data']['_separator'],  # Matches the generic separator
    '.*',  # Matches any character
]

# If the user requests to blocklist a specific QR code
if ROLLBACK_OR_BLOCKLIST == '1':
    # Takes user input for tablet serial number
    TABLET_SERIAL_NUMBER = input('Enter the tablet serial number of the QR code to delete: ')
    # Modifies the regex pattern elements to include the tablet serial number
    PATTERN_ELEMENTS.insert(
        1, (SCHEMA['generic_data']['serial_number'][0] + TABLET_SERIAL_NUMBER + '.*')
    )

# Stores all regex pattern objects
PATTERNS = []

# Compiles PATTERN_ELEMENTS into a regex pattern object
PATTERN = PATTERNS.append(re.compile(''.join(PATTERN_ELEMENTS)))

# Stores the already blocklisted QR codes from the local database
BLOCKLISTED_QRS = db.find('raw_qr', {'blocklisted': True})

# Counts the numbers of QR codes newly blocklisted in this run
num_blocklisted = 0

for qr_code in db.find('raw_qr'):
    # If the QR code is already blocklisted, go to the next QR code
    if qr_code in BLOCKLISTED_QRS:
        continue
    # Iterates through all regex pattern objects
    for PATTERN in PATTERNS:
        if re.search(PATTERN, qr_code) is None:
            # If the pattern doesn't match, go to the next QR code
            break
    # If none of the other statements are true, blocklist it
    else:
        # Uses the update_qr_blocklist_status function to change the value of blocklisted to True
        db.update_qr_blocklist_status({'data': qr_code['data']})
        num_blocklisted += 1

if num_blocklisted == 0:
    print('No QR codes were blocklisted')
else:
    print(f'Successfully blocklisted {num_blocklisted} QR codes')
