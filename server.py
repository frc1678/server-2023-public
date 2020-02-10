#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Main server file. Runs computations in infinite loop.

Runs on an Ubuntu 18.04 LTS computer in the stands at
competition. This script runs all of the computations in the server.
"""
# External imports
import json
import os
import re
# Internal imports
import adb_compressed_qr_data_puller
import decompressor
import cloud_database_communicator
import local_database_communicator
import qr_code_uploader
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
MAIN_QUEUE['raw']['qr'].extend(
    local_database_communicator.select_from_within_array('raw.qr')[0]['raw']['qr']
)

BLACKLISTED = local_database_communicator.select_from_within_array(
    'processed.replay_outdated_qr')[0]['processed']['replay_outdated_qr']
# Selecting only the non-blacklisted ones
MAIN_QUEUE['raw']['qr'] = [qr for qr in MAIN_QUEUE['raw']['qr'] if qr not in BLACKLISTED]

# Open the tablet serials file to find all device serials
with open('data/tablet_serials.json') as serial_numbers:
    DEVICE_SERIAL_NUMBERS = json.load(serial_numbers)

while True:
    # Parses 'adb devices' to find num of devices so that don't try to pull from nothing
    if len(utils.run_command('adb devices', True).split('\n')) != 1:
        TABLET_QR_DATA, DEVICE_FILE_PATHS = [], []
        DEVICE_FILE_PATH = 'data/tablets'
        # Pull all files from the 'Download' folder on the tablet
        adb_compressed_qr_data_puller.adb_pull_tablet_data(DEVICE_FILE_PATH,
                                                           '/storage/emulated/0/Download')
        # Iterates through the 'data' folder
        for device_dir in os.listdir(DEVICE_FILE_PATH):
            if device_dir in DEVICE_SERIAL_NUMBERS.keys():
                DEVICE_FILE_PATHS.append(device_dir)
            # If the folder name is a device serial, it must be a tablet folder
        for device in DEVICE_FILE_PATHS:
            # Iterate through the downloads folder in the device folder
            for file in os.listdir(f'{DEVICE_FILE_PATH}/{device}/Download'):
                # Makes a regex pattern that matches the file name of a QR file
                # Format of obj QR file pattern: <qual_num>_<team_num>_<serial_num>_<timestamp>.txt
                obj_pattern = re.compile(r'[0-9]+_[0-9]+_[A-Z0-9]+_[0-9]+.txt')
                # Format of subj QR file pattern: <qual_num>_<serial_num_<timestamp>.txt
                subj_pattern = re.compile(r'[0-9]+_[0-9A-Z]+_[0-9]+.txt')
                if re.fullmatch(obj_pattern, file) is not None or \
                        re.fullmatch(subj_pattern, file) is not None:
                    with open(f'{DEVICE_FILE_PATH}/{device}/Download/{file}') as qr_code_file:
                        qr_code = qr_code_file.read()
                        # If the QR code has a newline at the end, remove it
                        qr_code = qr_code.rstrip('\n')
                        # If the QR code isn't blacklisted or already in MAIN_QUEUE add it
                        if qr_code not in BLACKLISTED and qr_code not in MAIN_QUEUE:
                            TABLET_QR_DATA.append(qr_code)
        # Add the QR codes to MAIN_QUEUE and upload them
        MAIN_QUEUE['raw']['qr'].extend(qr_code_uploader.upload_qr_codes(TABLET_QR_DATA))
    RAW_SCANNER = input('Scan Data Here: ')
    # Do not try to upload blank string
    if RAW_SCANNER != '':
        QR_DATA = RAW_SCANNER.rstrip('\t').split('\t')
        # Upload QRs to MongoDB and add uploaded QRs to queue
        MAIN_QUEUE['raw']['qr'].extend(qr_code_uploader.upload_qr_codes(QR_DATA))

    # Decompress all inputted QRs
    DECOMPRESSED_QRS = decompressor.decompress_qrs(MAIN_QUEUE['raw']['qr'])
    # Update database with decompressed objective QRs
    local_database_communicator.append_document(
        DECOMPRESSED_QRS['unconsolidated_obj_tim'], 'processed.unconsolidated_obj_tim'
    )
    # Update database with decompressed subjective QRs
    local_database_communicator.append_document(
        DECOMPRESSED_QRS['subj_aim'], 'processed.subj_aim'
    )
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

    # TODO Pull Matches from TBA

    # TODO: Consolidation

    # TODO: TIM calcs

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
