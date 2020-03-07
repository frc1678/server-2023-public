#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Adds QR codes to a blacklist in the local database based on match number or blacklists
a specific QR code based on match number and tablet serial number.

If rollback match is selected, all QR codes from matches with the user inputted match number are
blacklisted. If blacklist a specific QR is selected, all QR codes from a specific
tablet serial number, and match number are added to the blacklist.
"""
# External imports
import sys
import re
# Internal imports
import utils
import local_database_communicator

# Takes user input to find which operation to do
ROLLBACK_OR_BLACKLIST = input('Rollback a match (0) or blacklist specific qrs (1)? (0,1): ')

# If user doesn't enter a valid option, exit
if ROLLBACK_OR_BLACKLIST not in ['0', '1']:
    print('Please enter a valid number')
    sys.exit()

print('WARNING: data from matching QR codes will be blacklisted or deleted')

# User input for match to delete
INVALID_MATCH = input('Enter the match to blacklist: ')

# If the user inputted match number is not a number, exit
if not INVALID_MATCH.isnumeric():
    print('Please enter a number')
    sys.exit()

# Opens the schema document, to be used in regex's
SCHEMA = utils.read_schema('schema/match_collection_qr_schema.yml')

# Stores all of the elements of the regex to be joined to a string later
PATTERN_ELEMENTS = [
    '.*',  # Matches any character
    SCHEMA['generic_data']['match_number'][0] + INVALID_MATCH,  # Matches the match number
    '\\' + SCHEMA['generic_data']['_separator'],  # Matches the generic separator
    '.*',  # Matches any character
]

# If the user requests to blacklist a specific QR code
if ROLLBACK_OR_BLACKLIST == '1':
    # Takes user input for tablet serial number
    TABLET_SERIAL_NUMBER = input('Enter the tablet serial number of the QR code to delete: ')
    # Modifies the regex pattern elements to include the tablet serial number
    PATTERN_ELEMENTS.insert(1,
                            (SCHEMA['generic_data']['serial_number'][0]
                             + TABLET_SERIAL_NUMBER + '.*'))

# Stores all regex pattern objects
PATTERNS = []

# Compiles PATTERN_ELEMENTS into a regex pattern object
PATTERN = PATTERNS.append(re.compile(''.join(PATTERN_ELEMENTS)))

# Stores the QRs that will be appended to the local database QR 'blacklist'
TO_BLACKLIST = []

# Takes TBA event key from utils.py
EVENT_KEY = utils.TBA_EVENT_KEY

# Stores the already blacklisted QR codes from the local database
BLACKLISTED_QRS = local_database_communicator.read_dataset('processed.replay_outdated_qr')

for qr_code in local_database_communicator.read_dataset('raw.qr'):
    # If the QR code is already blacklisted, go to the next QR code
    if qr_code in BLACKLISTED_QRS:
        continue
    # Iterates through all regex pattern objects
    for PATTERN in PATTERNS:
        if re.search(PATTERN, qr_code) is None:
            # If the pattern doesn't match, go to the next QR code
            break
    # If none of the other statements are true, add it to to_blacklist
    else:
        TO_BLACKLIST.append(qr_code)

# Uses append_document to add the QR codes to the local competition document blacklist
local_database_communicator.append_or_overwrite('processed.replay_outdated_qr', TO_BLACKLIST)

if not TO_BLACKLIST:
    print('No QR codes were blacklisted')
else:
    print(f'Successfully blacklisted {len(TO_BLACKLIST)} QR codes')
