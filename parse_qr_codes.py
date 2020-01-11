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

def parse_qr_codes(qr_data):
    """Parses QR codes and inserts them into the competition document.

    Splits QR codes into objective and subjective.
    Checks for duplicates within set of QR codes to add, and the set of QR codes to add and the
    database.
    Appends new QR codes to raw.obj and raw.subj
    """

    # Reads the schema file so that it can be accessed as a dictionary later
    with open(create_file_path('schema/match_collection_qr_schema.yml', False)) as schema_file:
        schema = yaml.load(schema_file, yaml.Loader)

    # Reads competition.txt file, which only contains the competition code, in order to find the
    # competition document
    with open('data/competition.txt') as file:
        competition_code = file.read()

    # Acquires the raw data from competition document
    db = MongoClient('localhost', 27017).scouting_system
    raw_data = db.competitions.find_one({'tba_event_code': competition_code})['raw']

    # Creates two lists to store QR codes separated into objective and subjective
    qr_obj = []
    qr_subj = []

    # Appends individual QR codes to QR_CODES
    # Checks the schema document for the starting character of subjective and objective QR codes,
    # and splits the QR codes into objective and subjective QR codes at the same time, if the QR
    # code isn't already the already split list, or already in the database it doesn't add it
    for qr_code in qr_data:
        if qr_code.startswith(schema['subjective']['_start_character']):
            if qr_code not in qr_subj and qr_code not in raw_data['qr_subj']:
                qr_subj.append(qr_code)
            else:
                print(f'Removed a duplicate subjective QR code: {qr_code}')
        elif qr_code.startswith(schema['objective_tim']['_start_character']):
            if qr_code not in qr_obj and qr_code not in raw_data['qr_obj']:
                qr_obj.append(qr_code)
            else:
                print(f'Removed a duplicate objective QR code: {qr_code}')
        else:
            raise ValueError('QR Code does not have a valid start character')

    # Adds the objective and subjective QR codes to the local database if the lists aren't empty
    if qr_obj != []:
        db.competitions.update_one({'tba_event_code': competition_code},
                                   {'$push': {'raw.qr_obj': {'$each': qr_obj}}})
    if qr_subj != []:
        db.competitions.update_one({'tba_event_code': competition_code},
                                   {'$push': {'raw.qr_subj': {'$each': qr_subj}}})
