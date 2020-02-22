#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Main server file. Runs computations in infinite loop.

Runs on an Ubuntu 18.04 LTS computer in the stands at
competition. This script runs all of the computations in the server.
"""
# No external imports
# Internal imports
import adb_communicator
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
            'obj_pit': [],
            'subj_pit': []
        },
        'processed': {
            'unconsolidated_obj_tim': [],
            'subj_aim': [],
            'calc_obj_tim': [],
            'calc_tba_tim': [],
            'calc_obj_team': [],
            'calc_tba_team': [],
            'calc_subj_team': [],
            'calc_match': []
        }
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
MAIN_QUEUE['raw']['qr'].extend(local_database_communicator.read_dataset('raw.qr'))

BLACKLISTED = local_database_communicator.read_dataset('processed.replay_outdated_qr')
# Selecting only the non-blacklisted ones
MAIN_QUEUE['raw']['qr'] = [qr for qr in MAIN_QUEUE['raw']['qr'] if qr not in BLACKLISTED]

# Add existing pit data to main queue on server restart
MAIN_QUEUE['raw']['obj_pit'] = [{'team_number': point['team_number']} for point in
                                local_database_communicator.read_dataset('raw.obj_pit')]
MAIN_QUEUE['raw']['subj_pit'] = [{'team_number': point['team_number']} for point in
                                 local_database_communicator.read_dataset('raw.subj_pit')]

# Where we get the match data from TBA
MATCH_LIST = []


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

    # Empty decompressed QRs in the database if this is the first cycle since server restart
    # Otherwise, decompressed QRs will potentially stack as server restarts could entail schema
    # or decompression code changes, and selection purely by team/match number would not work as
    # there are multiple QRs for a match
    if SERVER_RESTART:
        local_database_communicator.remove_data('processed.unconsolidated_obj_tim')
        local_database_communicator.remove_data('processed.subj_aim')
        local_database_communicator.remove_data('processed.calc_obj_tim')

    # Decompress all inputted QRs
    DECOMPRESSED_QRS = decompressor.decompress_qrs(MAIN_QUEUE['raw']['qr'])
    # Update database with decompressed objective QRs
    local_database_communicator.append_or_overwrite(
        'processed.unconsolidated_obj_tim', DECOMPRESSED_QRS['unconsolidated_obj_tim'])
    # Update database with decompressed subjective QRs
    local_database_communicator.append_or_overwrite(
        'processed.subj_aim', DECOMPRESSED_QRS['subj_aim'])
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
    # Makes a list of matches that have been retrieved
    # match is a single dictionary from TBA_MATCH_DATA
    for match in TBA_MATCH_DATA:
        # match_key looks through match to find the match number and type
        # Checks that we are only getting the qualification matches
        if match['comp_level'] == 'qm':
            if match.get('actual_time', 0) != 0 and match['match_number'] not in MATCH_LIST:
                MATCH_LIST.append(match['match_number'])
                MAIN_QUEUE['processed']['calc_tba_tim'].append(
                    {'match_number': int(match['match_number'])})
                TEAMS = [match['alliances'][alliance]['team_keys'] for alliance in ['red', 'blue']]
                for alliance in TEAMS:
                    for team in alliance:
                        team = {'team_number': int(team[3:])}
                        if team not in MAIN_QUEUE['processed']['calc_tba_team']:
                            MAIN_QUEUE['processed']['calc_tba_team'].append(team)

    # Where we get the rankings from TBA
    TBA_RANKINGS_DATA = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/rankings')

    # Consolidate & calculate TIMs for each match in the main queue
    calculated_obj_tims = calculate_tims.update_calc_obj_tims(
        MAIN_QUEUE['processed']['unconsolidated_obj_tim'])
    MAIN_QUEUE['processed']['calc_obj_tim'] = calculated_obj_tims
    local_database_communicator.append_or_overwrite('processed.calc_obj_tim', calculated_obj_tims)
    matches_to_be_calculated = set()
    teams_to_be_calculated = set()
    for tim in calculated_obj_tims:
        matches_to_be_calculated.add(tim['match_number'])
        teams_to_be_calculated.add(tim['team_number'])
    MAIN_QUEUE['processed']['calc_match'] = [
        {'match_number': match} for match in matches_to_be_calculated]
    MAIN_QUEUE['processed']['calc_obj_team'] = [
        {'team_number': team} for team in teams_to_be_calculated]

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

    if SERVER_RESTART:
        SERVER_RESTART = False
