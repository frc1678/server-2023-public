#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Updates local database with data pulled from cloud DB."""

import re
import sys

import cloud_database_communicator
import local_database_communicator
import utils

CONFIRMATION = input(f'Confirm Overwrite of data in {utils.TBA_EVENT_KEY}? (y/N): ')
if CONFIRMATION.lower() not in ['y', 'yes']:
    print('Aborting...')
    sys.exit(1)

EVENT = input(f'Enter event code to pull data from. Leave blank to use {utils.TBA_EVENT_KEY}: ')
if EVENT == '':
    EVENT = utils.TBA_EVENT_KEY
    print(f'Using event code {EVENT}')
elif not re.fullmatch('[0-9]{4}[a-z0-9]+', EVENT):
    raise ValueError(f'Invalid event code {EVENT}')

CLOUD_DATA = cloud_database_communicator.CLOUD_DB.competitions.find_one(
    {'tba_event_key': EVENT}, {'_id': 0})
if CLOUD_DATA is None:
    print(f'Event {EVENT} missing from Cloud Database')
    sys.exit(1)
local_database_communicator.DB.competitions.update_one(
    {'tba_event_key': EVENT}, {'$set': CLOUD_DATA}, upsert=True)

utils.log_info(f'Pulled data from {EVENT} to {utils.TBA_EVENT_KEY}')
print('Data fetch successful')
