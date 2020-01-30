#!/usr/bin/python3.6
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Main server file. Runs computations in infinite loop.

Runs on an Ubuntu 18.04 LTS computer in the stands at
competition. This script runs all of the computations in the server.
"""
# No external imports
# Internal imports
import decompressor
import local_database_communicator
import qr_code_uploader


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


CLOUD_DB_QUEUE = get_empty_modified_data()
MAIN_QUEUE = get_empty_modified_data()
MAIN_QUEUE['raw']['qr'].extend(
    local_database_communicator.select_from_within_array('raw.qr')[0]['raw']['qr']
)

while True:
    RAW_SCANNER = input('Scan Data Here: ')
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
    for qr_type in DECOMPRESSED_QRS:
        MAIN_QUEUE['processed'][qr_type].extend(DECOMPRESSED_QRS[qr_type])

    # TODO Pull Matches from TBA

    # TODO: Consolidation

    # TODO: TIM calcs

    # TODO: Team calcs

    # TODO: Pull rankings from TBA

    # TODO: Match calcs

    # TODO: Team calcs (driver ability)

    # TODO: Send data to cloud DB
    # Merge CLOUD_DB_QUEUE and MAIN_QUEUE
    for key in MAIN_QUEUE:
        for dataset, data in MAIN_QUEUE[key].items():
            CLOUD_DB_QUEUE[key][dataset].extend(data)
    # Empty main queue
    MAIN_QUEUE = get_empty_modified_data()
