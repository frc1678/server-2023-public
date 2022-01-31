#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Updates local database with data pulled from cloud DB."""

import re
import sys

import termcolor

from data_transfer import cloud_db_updater
from server import Server
import utils

termcolor.cprint(
    'WARNING: This script does not currently work on the new database structure',
    color='yellow',
)

CONFIRMATION = input(f'Confirm Overwrite of data in {Server.TBA_EVENT_KEY}? (y/N): ')
if CONFIRMATION.lower() not in ['y', 'yes']:
    print('Aborting...', file=sys.stderr)
    sys.exit(1)

EVENT = input(f'Enter event code to pull data from. Leave blank to use {Server.TBA_EVENT_KEY}: ')

if EVENT == '':
    EVENT = Server.TBA_EVENT_KEY
    print(f'Using event code {EVENT}')
elif not re.fullmatch('[0-9]{4}[a-z0-9]+', EVENT):
    raise ValueError(f'Invalid event code {EVENT}')
# TODO Update this for new db structure
# CLOUD_DATA = cloud_db_updater.CLOUD_DB.competitions.find_one({'tba_event_key': EVENT}, {'_id': 0})
# if CLOUD_DATA is None:
#     print(f'Event {EVENT} missing from Cloud Database', file=sys.stderr)
#     sys.exit(1)
# TODO: don't use ldc
# ldc.DB.competitions.update_one({'tba_event_key': EVENT}, {'$set': CLOUD_DATA}, upsert=True)
# utils.log_info(f'Pulled data from {EVENT} to {Server.TBA_EVENT_KEY}')
# print('Data fetch successful')
