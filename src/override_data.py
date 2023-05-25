#!/usr/bin/env python3

"""Adds QR codes to a blocklist in the local database based on match number, blocklists
a specific QR code based on match number and tablet serial number, or overrides datatapoins
for specific TIMs based on match number and team number.

If rollback match is selected, all QR codes from matches with the user inputted match number are
blocklisted. If blocklist a specific QR is selected, all QR codes from a specific
tablet serial number, and match number are added to the blocklist. If edit team data for a
specific match is selected, all QR codes from a specific TIM are overriden.
"""

import re
import sys

from data_transfer import database
import utils

db = database.Database()

# Takes user input to find which operation to do
ROLLBACK_BLOCKLIST_OR_DATA = input(
    "Rollback a match (0), blocklist specific qrs (1), or edit team data for a specific match (2)? (0,1,2): "
)

# If user doesn't enter a valid option, exit
if ROLLBACK_BLOCKLIST_OR_DATA not in ["0", "1", "2"]:
    print("Please enter a valid number", file=sys.stderr)
    sys.exit()

# Find if the user wants to UNDO this action
UNDO = input(
    f"Do you want to {'UNDO blocklisting' if ROLLBACK_BLOCKLIST_OR_DATA != '2' else 'CLEAR overrides on'} this {['match', 'qr', 'team'][int(ROLLBACK_BLOCKLIST_OR_DATA)]}? (y/N)"
)
UNDO = UNDO.lower() == "y"

print(
    f"WARNING: data from matching QR codes will be {'un' if UNDO else ''}{'blocklisted' if ROLLBACK_BLOCKLIST_OR_DATA != '2' else 'overriden'}"
)

# User input for match to delete
INVALID_MATCH = input("Enter the match to blocklist: ")

# If the user inputted match number is not a number, exit
if not INVALID_MATCH.isnumeric():
    print("Please enter a number")
    sys.exit()

# Opens the schema document, to be used in regexes
SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")

# Stores all of the elements of the regex to be joined to a string later
PATTERN_ELEMENTS = [
    ".*",  # Matches any character
    SCHEMA["generic_data"]["match_number"][0] + INVALID_MATCH,  # Matches the match number
    "\\" + SCHEMA["generic_data"]["_separator"],  # Matches the generic separator
    ".*",  # Matches any character
]

# If the user requests to blocklist a specific QR code
if ROLLBACK_BLOCKLIST_OR_DATA == "1":
    # Takes user input for scout name
    SCOUT_NAME = input("Enter the scout name of the QR code to blocklist: ")
    # Modifies the regex pattern elements to include the scout name
    PATTERN_ELEMENTS.insert(4, (SCHEMA["generic_data"]["scout_name"][0] + SCOUT_NAME + ".*"))
elif ROLLBACK_BLOCKLIST_OR_DATA == "2":
    # Takes user input for team name
    TEAM_NAME = input("Enter the team number of the TIM data to edit: ")
    PATTERN_ELEMENTS.insert(4, (SCHEMA["objective_tim"]["team_number"][0] + TEAM_NAME + ".*"))
    # Takes user input for data point name
    DATA_NAME = input(f"Enter the name of the TIM data point to edit for {TEAM_NAME}: ")
    # Takes user input for the new value
    NEW_VALUE = input(
        f'Enter the new value for the data point {DATA_NAME} (input is converted to int/float/bool if possible unless in ""): '
    )
    if NEW_VALUE.isdecimal():
        NEW_VALUE = int(NEW_VALUE)
    elif "." in NEW_VALUE and NEW_VALUE.replace(".", "0", 1).isdecimal():
        NEW_VALUE = float(NEW_VALUE)
    elif (l := NEW_VALUE.lower()) in ["true", "false"]:
        NEW_VALUE = {"true": True, "false": False}[l]
    elif NEW_VALUE[0] == NEW_VALUE[-1] == '"':
        NEW_VALUE = NEW_VALUE[1:-1]

# Stores all regex pattern objects
PATTERNS = []

# Compiles PATTERN_ELEMENTS into a regex pattern object
PATTERNS.append(re.compile("".join(PATTERN_ELEMENTS)))

# Stores the already blocklisted QR codes from the local database
BLOCKLISTED_QRS = db.find("raw_qr", {"blocklisted": True})

# Counts the numbers of QR codes newly blocklisted in this run
num_blocklisted = 0

for qr_code in db.find("raw_qr"):
    # If the QR code is already blocklisted, go to the next QR code
    if (not UNDO) and qr_code in BLOCKLISTED_QRS:
        continue
    # Iterates through all regex pattern objects
    for PATTERN in PATTERNS:
        if re.search(PATTERN, qr_code["data"]) is None:
            # If the pattern doesn't match, go to the next QR code
            break
    # If none of the other statements are true, blocklist it
    else:
        if ROLLBACK_BLOCKLIST_OR_DATA == "2":
            # Uses the update_qr_data_override function to change the value of override[DATA_NAME] to NEW_VALUE
            db.update_qr_data_override(
                {"data": qr_code["data"]}, DATA_NAME, NEW_VALUE, clear=not UNDO
            )
        else:
            # Uses the update_qr_blocklist_status function to change the value of blocklisted to True, or False if undoing
            db.update_qr_blocklist_status({"data": qr_code["data"]}, blocklist=not UNDO)
        num_blocklisted += 1

if num_blocklisted == 0:
    print(f"No QR codes were {'Overriden' if ROLLBACK_BLOCKLIST_OR_DATA == '2' else 'Blocklisted'}")
else:
    print(
        f"Successfully {'Overriden' if ROLLBACK_BLOCKLIST_OR_DATA == '2' else 'Blocklisted'} {num_blocklisted} QR codes"
    )
