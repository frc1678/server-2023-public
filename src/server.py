#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Main server file. Runs computations in infinite loop.

Runs on an Ubuntu 18.04 LTS computer in the stands at competition. This script runs all of the
computations in the server.
"""

import sys

import pymongo

from calculations import decompressor, obj_team, obj_tims, tba_tims, tba_team
from data_transfer import adb_communicator, local_database_communicator as ldc, tba_communicator
import qr_code_uploader
import utils

try:
    from data_transfer import cloud_database_communicator
except pymongo.errors.ConfigurationError:
    utils.log_warning(f'Cloud database import failed. No internet.')


def get_empty_modified_data():
    """Returns empty modified data field."""
    modified_data = {
        'raw': {'qr': [], 'obj_pit': [], 'subj_pit': []},
        'processed': {
            'unconsolidated_obj_tim': [],
            'calc_obj_tim': [],
            'calc_tba_tim': [],
            'subj_aim': [],
            'calc_obj_team': [],
            'calc_subj_team': [],
            'calc_match': [],
            'calc_predicted_aim': [],
            'calc_predicted_team': [],
            'calc_tba_team': [],
            'calc_pickability_team': [],
        },
    }
    return modified_data


# Tracks if cloud database has been updated since the latest server restart
# Is used to determine if raw.qr should be completely emptied or just pushed to
SERVER_RESTART_SINCE_CLOUD_UPDATE = True
# Tracks if this is the first calculation cycle since server restart
SERVER_RESTART = True
# Instantiate the queue that stores what changes need to be pushed to cloud
CLOUD_DB_QUEUE = get_empty_modified_data()
# Instantiate the queue that tracks what data has been changed
# This queue is used to determine what calculations need to be run and what data to run them on.
MAIN_QUEUE = get_empty_modified_data()
MAIN_QUEUE['raw']['qr'].extend(ldc.read_dataset('raw.qr'))

BLOCKLISTED = ldc.read_dataset('processed.replay_outdated_qr')
# Selecting only the non-blocklisted ones
MAIN_QUEUE['raw']['qr'] = [qr for qr in MAIN_QUEUE['raw']['qr'] if qr not in BLOCKLISTED]

# Add existing pit data to main queue on server restart
MAIN_QUEUE['raw']['obj_pit'] = [
    {'team_number': point['team_number']} for point in ldc.read_dataset('raw.obj_pit')
]
MAIN_QUEUE['raw']['subj_pit'] = [
    {'team_number': point['team_number']} for point in ldc.read_dataset('raw.subj_pit')
]

# Where we get the match data from TBA
MATCH_LIST = []

while True:
    USER_INPUT = input(
        'Do you want to run server with write permission to cloud database?\n'
        '(If so, make sure you are on the server computer or that no one else is '
        'currently writing to the cloud database) [Y/n]'
    ).lower()
    if USER_INPUT == 'y':
        CLOUD_WRITE_PERMISSION = True
        break
    if USER_INPUT == 'n':
        CLOUD_WRITE_PERMISSION = False
        break
    print('Please be sure to enter either "y" or "n"')

while True:
    # TODO Pull team pictures from tablets
    TABLET_DATA = adb_communicator.pull_device_data()
    for dataset, refs in TABLET_DATA.items():
        MAIN_QUEUE['raw'][dataset].extend(refs)
    RAW_SCANNER = input('Scan Data Here: ')
    # Do not try to upload blank string
    if RAW_SCANNER != '':
        QR_DATA = RAW_SCANNER.rstrip('\t').split('\t')
        # Upload QRs to MongoDB and add uploaded QRs to queue
        MAIN_QUEUE['raw']['qr'].extend(qr_code_uploader.upload_qr_codes(QR_DATA))

    # Empty decompressed QRs in the database if this is the first cycle since server restart.
    # Otherwise, decompressed QRs will potentially stack as server restarts could entail schema
    # or decompression code changes, and selection purely by team/match number would not work as
    # there are multiple QRs for a match.
    if SERVER_RESTART:
        ldc.remove_data('processed.unconsolidated_obj_tim')
        ldc.remove_data('processed.subj_aim')
        ldc.remove_data('processed.calc_obj_tim')

    # Decompress all inputted QRs
    DECOMPRESSED_QRS = decompressor.decompress_qrs(MAIN_QUEUE['raw']['qr'])
    # Update database with decompressed objective QRs
    ldc.append_to_dataset(
        'processed.unconsolidated_obj_tim', DECOMPRESSED_QRS['unconsolidated_obj_tim']
    )
    # Update database with decompressed subjective QRs
    ldc.append_to_dataset('processed.subj_aim', DECOMPRESSED_QRS['subj_aim'])
    # Add decompressed QRs to queues
    # Iterate through both objective and subjective QRs
    for qr_type in DECOMPRESSED_QRS:
        for qr in DECOMPRESSED_QRS[qr_type]:
            # Include match number in information to be added to queue
            QR_ID = {'match_number': qr['match_number']}
            # Only include team number for objective QRs
            if qr_type == 'unconsolidated_obj_tim':
                QR_ID['team_number'] = qr['team_number']
            # Only add QR if it is not already in queue
            if QR_ID not in MAIN_QUEUE['processed'][qr_type]:
                MAIN_QUEUE['processed'][qr_type].append(QR_ID)

    # Notify about missing data
    decompressor.check_scout_ids()

    # TBA_MATCH_DATA is a list of dictionaries
    TBA_MATCH_DATA = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/matches')
    if TBA_MATCH_DATA is None:
        TBA_MATCH_DATA = []
    NEW_TBA_MATCHES = []
    # Makes a list of matches that have been retrieved
    # match is a single dictionary from TBA_MATCH_DATA
    for match in TBA_MATCH_DATA:
        # match_key looks through match to find the match number and type
        # Checks that we are only getting the qualification matches
        if match['comp_level'] == 'qm':
            if match.get('actual_time', 0) != 0 and match['match_number'] not in MATCH_LIST:
                NEW_TBA_MATCHES.append({'match_number': match['match_number']})
    MATCH_LIST.extend(NEW_TBA_MATCHES)

    # TBA TIM Calcs
    CALCULATED_TBA_TIMS = tba_tims.update_calc_tba_tims(NEW_TBA_MATCHES)
    for tim in CALCULATED_TBA_TIMS:
        query = {'match_number': tim['match_number'], 'team_number': tim['team_number']}
        ldc.update_dataset('processed.calc_tba_tim', tim, query)
    MAIN_QUEUE['processed']['calc_tba_tim'] = [
        {'match_number': tim['match_number'], 'team_number': tim['team_number']}
        for tim in CALCULATED_TBA_TIMS
    ]

    # Where we get the rankings from TBA
    TBA_RANKINGS_DATA = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/rankings')

    # Consolidate & calculate TIMs for each match in the main queue
    CALCULATED_OBJ_TIMS = obj_tims.update_calc_obj_tims(
        MAIN_QUEUE['processed']['unconsolidated_obj_tim']
    )
    MAIN_QUEUE['processed']['calc_obj_tim'] = [
        {'team_number': tim['team_number'], 'match_number': tim['match_number']}
        for tim in CALCULATED_OBJ_TIMS
    ]
    for tim in CALCULATED_OBJ_TIMS:
        query = {'match_number': tim['match_number'], 'team_number': tim['team_number']}
        ldc.update_dataset('processed.calc_obj_tim', tim, query)
        MAIN_QUEUE['processed']['calc_obj_tim'].append(
            {'match_number': tim['match_number'], 'team_number': tim['team_number']}
        )

    for ref in MAIN_QUEUE['processed']['calc_obj_tim']:
        team = ref['team_number']
        calculated_team = utils.catch_function_errors(obj_team.calculate_obj_team, team)
        if calculated_team is not None:
            ldc.update_dataset(
                'processed.calc_obj_team', calculated_team, query={'team_number': team}
            )
            CALC_TEAM_REF = {'team_number': team}
            if CALC_TEAM_REF not in MAIN_QUEUE['processed']['calc_obj_team']:
                MAIN_QUEUE['processed']['calc_obj_team'].append(CALC_TEAM_REF)

    # Make TBA Team request to update team names
    tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/teams/simple')

    TBA_TEAM_CALCS = tba_team.update_team_calcs(
        MAIN_QUEUE['processed']['calc_obj_tim'] + MAIN_QUEUE['processed']['calc_tba_tim']
    )
    for calc in TBA_TEAM_CALCS:
        TBA_TEAM_REF = {'team_number': calc['team_number']}
        ldc.update_dataset('processed.calc_tba_team', calc, TBA_TEAM_REF)
        MAIN_QUEUE['processed']['calc_tba_team'].append(TBA_TEAM_REF)

    # TODO: Match calcs

    # TODO: Team calcs (driver ability)
    if 'data_transfer.cloud_database_communicator' not in sys.modules:
        try:
            from data_transfer import cloud_database_communicator
        except pymongo.errors.ConfigurationError:
            utils.log_warning(f'Cloud database import failed. No internet.')

    # Send data to cloud database
    # Merge CLOUD_DB_QUEUE and MAIN_QUEUE
    for key in MAIN_QUEUE:
        for dataset, data in MAIN_QUEUE[key].items():
            CLOUD_DB_QUEUE[key][dataset].extend(data)
    # Empty main queue
    MAIN_QUEUE = get_empty_modified_data()
    # Send data to cloud
    if (
        'data_transfer.cloud_database_communicator' in sys.modules
        and CLOUD_WRITE_PERMISSION is True
    ):
        CLOUD_WRITE_RESULT = cloud_database_communicator.push_changes_to_db(
            CLOUD_DB_QUEUE, SERVER_RESTART_SINCE_CLOUD_UPDATE
        )
        if CLOUD_WRITE_RESULT is not None:
            CLOUD_DB_QUEUE = get_empty_modified_data()
            if SERVER_RESTART_SINCE_CLOUD_UPDATE:
                SERVER_RESTART_SINCE_CLOUD_UPDATE = False

    SERVER_RESTART = False
