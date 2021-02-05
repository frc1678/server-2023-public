#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Updates local database with data pulled from cloud DB."""

import re
import sys

import termcolor

from data_transfer import local_database_communicator as ldc, cloud_db_updater
import utils

termcolor.cprint(
    'WARNING: This script does not currently work on the new database structure', color='yellow'
)

CONFIRMATION = input(f'Confirm Overwrite of data in {utils.TBA_EVENT_KEY}? (y/N): ')
if CONFIRMATION.lower() not in ['y', 'yes']:
    print('Aborting...', file=sys.stderr)
    sys.exit(1)

EVENT = input(f'Enter event code to pull data from. Leave blank to use {utils.TBA_EVENT_KEY}: ')
if EVENT == '':
    EVENT = utils.TBA_EVENT_KEY
    print(f'Using event code {EVENT}')
elif not re.fullmatch('[0-9]{4}[a-z0-9]+', EVENT):
    raise ValueError(f'Invalid event code {EVENT}')

# TODO Update this for new db structure
# CLOUD_DATA = cloud_db_updater.CLOUD_DB.competitions.find_one({'tba_event_key': EVENT}, {'_id': 0})
# if CLOUD_DATA is None:
#     print(f'Event {EVENT} missing from Cloud Database', file=sys.stderr)
#     sys.exit(1)
# ldc.DB.competitions.update_one({'tba_event_key': EVENT}, {'$set': CLOUD_DATA}, upsert=True)

# utils.log_info(f'Pulled data from {EVENT} to {utils.TBA_EVENT_KEY}')
# print('Data fetch successful')
