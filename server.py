#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Main server file. Runs computations in infinite loop.

Runs on an Ubuntu 18.04 LTS computer in the stands at
competition. This script runs all of the computations in the server.
"""
# No external imports
# Internal imports
import calculate_tims
import decompressor
import cloud_database_communicator
import local_database_communicator
import qr_code_uploader
import tba_communicator
import utils


def get_empty_modified_data():
    """Returns empty modified data field."""
    modified_data = {
        'raw': {
            'qr': [],
            'pit': []
        },
        'processed': {
            'unconsolidated_obj_tim': [],
            'consolidated_obj_tim': [],
            'subj_aim': [],
            'calc_obj_tim': [],
            'calc_team': [],
            'calc_match': []
        }
    }
    return modified_data


# Tracks if cloud database has been updated since the latest server restart
# Is used to determine if raw.qr should be completely emptied or just pushed to
SERVER_RESTART_SINCE_CLOUD_UPDATE = True
# Instantiate the queue that stores what changes need to be pushed to cloud
CLOUD_DB_QUEUE = get_empty_modified_data()
# Instantiate the queue that tracks what data has been changed
# This queue is used to determine what calculations need to be run and what data to run them on.
MAIN_QUEUE = get_empty_modified_data()
MAIN_QUEUE['raw']['qr'].extend(local_database_communicator.read_dataset('raw.qr'))

BLACKLISTED = local_database_communicator.read_dataset('processed.replay_outdated_qr')
# Selecting only the non-blacklisted ones
MAIN_QUEUE['raw']['qr'] = [qr for qr in MAIN_QUEUE['raw']['qr'] if qr not in BLACKLISTED]

# Where we get the match data from TBA
MATCH_LIST = []

while True:
    RAW_SCANNER = input('Scan Data Here: ')
    # Do not try to upload blank string
    if RAW_SCANNER != '':
        QR_DATA = RAW_SCANNER.rstrip('\t').split('\t')
        # Upload QRs to MongoDB and add uploaded QRs to queue
        MAIN_QUEUE['raw']['qr'].extend(qr_code_uploader.upload_qr_codes(QR_DATA))

    # Decompress all inputted QRs
    DECOMPRESSED_QRS = decompressor.decompress_qrs(MAIN_QUEUE['raw']['qr'])
    # Update database with decompressed objective QRs
    local_database_communicator.append_or_overwrite(
        'processed.unconsolidated_obj_tim', DECOMPRESSED_QRS['unconsolidated_obj_tim'])
    # Update database with decompressed subjective QRs
    local_database_communicator.append_or_overwrite(
        'processed.subj_aim', DECOMPRESSED_QRS['subj_aim'])
    # Add decompressed QRs to queues
    for qr_type in DECOMPRESSED_QRS:
        MAIN_QUEUE['processed'][qr_type].extend(DECOMPRESSED_QRS[qr_type])

    # TBA_MATCH_DATA is a list of dictionaries
    TBA_MATCH_DATA = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/matches')
    # Makes a list of matches that have been retrieved
    # match is a single dictionary from TBA_MATCH_DATA
    for match in TBA_MATCH_DATA:
        # match_key looks through match to find the match number and type
        # Checks that we are only getting the qualification matches
        if match['comp_level'] == 'qm':
            if match.get('actual_time', 0) != 0 and match['match_number'] not in MATCH_LIST:
                MATCH_LIST.append(match['match_number'])
                MAIN_QUEUE['processed']['unconsolidated_obj_tim'].append(
                    {'match_number': int(match['match_number'])})
    # Where we get the rankings from TBA
    TBA_RANKINGS_DATA = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/rankings')

    # Consolidate & calculate TIMs for each match in the main queue
    calculated_obj_tims = calculate_tims.update_calc_obj_tims(
        MAIN_QUEUE['processed']['unconsolidated_obj_tim'])
    MAIN_QUEUE['processed']['calc_obj_tim'] = calculated_obj_tims

    # TODO: Team calcs

    # TODO: Pull rankings from TBA

    # TODO: Match calcs

    # TODO: Team calcs (driver ability)

    # Send data to cloud database
    # Merge CLOUD_DB_QUEUE and MAIN_QUEUE
    for key in MAIN_QUEUE:
        for dataset, data in MAIN_QUEUE[key].items():
            CLOUD_DB_QUEUE[key][dataset].extend(data)
    # Empty main queue
    MAIN_QUEUE = get_empty_modified_data()
    # Send data to cloud
    CLOUD_WRITE_RESULT = cloud_database_communicator.push_changes_to_db(
        CLOUD_DB_QUEUE, SERVER_RESTART_SINCE_CLOUD_UPDATE
    )
    # push_changes_to_db returns None on connection errors
    if CLOUD_WRITE_RESULT is not None:
        CLOUD_DB_QUEUE = get_empty_modified_data()
        if SERVER_RESTART_SINCE_CLOUD_UPDATE:
            SERVER_RESTART_SINCE_CLOUD_UPDATE = False
