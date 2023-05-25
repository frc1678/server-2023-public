#!/usr/bin/env python3

"""Updates local database with data pulled from cloud DB."""

import re
import sys

from server import Server

import logging

from rich.prompt import Confirm, Prompt

log = logging.getLogger(__name__)

log.warning(
    "This script does not currently work on the new database structure",
)

if not Confirm.ask(f"Confirm Overwrite of data in {Server.TBA_EVENT_KEY}?", default=False):
    log.fatal("Aborting...")
    sys.exit(1)

EVENT = Prompt.ask(f"Enter event code to pull data from", default=Server.TBA_EVENT_KEY)

if not re.fullmatch("[0-9]{4}[a-z0-9]+", EVENT):
    raise ValueError(f"Invalid event code {EVENT}")
# TODO Update this for new db structure
# CLOUD_DATA = cloud_db_updater.CLOUD_DB.competitions.find_one({'tba_event_key': EVENT}, {'_id': 0})
# if CLOUD_DATA is None:
#     print(f'Event {EVENT} missing from Cloud Database', file=sys.stderr)
#     sys.exit(1)
# TODO: don't use ldc
# ldc.DB.competitions.update_one({'tba_event_key': EVENT}, {'$set': CLOUD_DATA}, upsert=True)
# log.info(f'Pulled data from {EVENT} to {Server.TBA_EVENT_KEY}')
# print('Data fetch successful')
