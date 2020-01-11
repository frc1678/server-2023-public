#!/usr/bin/python3.6
"""Houses parse_qr_codes() which parses and appends unique QR codes to local competition document

Splits QR codes into objective and subjective.
Checks for duplicates within set of QR codes to add, and the set of QR codes to add and the
database.
Appends new QR codes to raw.obj and raw.subj
"""
# External imports
import yaml
from pymongo import MongoClient
# Internal imports
from utils import create_file_path

def upload_qr_codes(qr_codes):
    """Uploads QR codes into the current competition document.

    Adds each QR code into its appropriate dataset.
    Prevents duplicate QR codes from being uploaded to the database.

    qr_codes is a list of QR code strings to upload
    """

    # Gets the starting character for each QR code type, used to identify QR code type
    with open(create_file_path('schema/match_collection_qr_schema.yml')) as schema_file:
        schema = yaml.load(schema_file, yaml.Loader)

    # Gets TBA event code of current competition
    with open('data/competition.txt') as file:
        competition_code = file.read()

    # Acquires the raw data from competition document
    db = MongoClient('localhost', 27017).scouting_system
    raw_data = db.competitions.find_one({'tba_event_code': competition_code})['raw']

    # Creates two lists to store QR codes separated into objective and subjective
    qr_obj = []
    qr_subj = []

    for qr_code in qr_codes:
        # Adds QR code to its dataset if it hasn't already been added
        # Identifies QR code type based on its first character
        if qr_code.startswith(schema['subjective']['_start_character']):
            if qr_code in qr_subj or qr_code in raw_data['qr_subj']:
                print(f'Duplicate QR code not uploaded: "{qr_code}"')
            else:
                qr_subj.append(qr_code)
        elif qr_code.startswith(schema['objective_tim']['_start_character']):
            if qr_code in qr_obj or qr_code in raw_data['qr_obj']:
                print(f'Duplicate QR code not uploaded: "{qr_code}"')
            else:
                qr_obj.append(qr_code)
        else:
            raise ValueError(f'Invalid QR code - no start character: "{qr_code}"')

    # Adds the objective and subjective QR codes to the local database if the lists aren't empty
    if qr_obj != []:
        db.competitions.update_one({'tba_event_code': competition_code},
                                   {'$push': {'raw.qr_obj': {'$each': qr_obj}}})
    if qr_subj != []:
        db.competitions.update_one({'tba_event_code': competition_code},
                                   {'$push': {'raw.qr_subj': {'$each': qr_subj}}})
