#!/usr/bin/python3.6
"""Parse data from qr_input.txt and upload it to MongoDB.
Reads QR codes from qr_input.txt, and splits it into objective and subjective QR codes.
Whilst splitting into objective and subjective QR codes, if the QR code is already in the already
split list, or in the local database, it simply isn't added to the split list.
When database entry is complete, qr_input.txt is deleted
"""
# External imports
from os import path, remove
import yaml
from pymongo import MongoClient
# Internal imports
from utils import create_file_path

if path.exists('data/qr_input.txt'):
    with open('data/qr_input.txt', 'r') as file:
        QR_DATA = file.read()
        if QR_DATA == '':
            raise ValueError('The input file is empty')

else:
    raise Exception('data/qr_input.txt does not exist, try running input_qr_codes.py first')

# '\t' refers to tab character, rstrip removes trailing tab from end mark of last QR code
QR_DATA = QR_DATA.rstrip('\t').split('\t')

# Reads the schema file so that it can be accessed as a dictionary later
with open(create_file_path('schema/match_collection_qr_schema.yml', False)) as schema_file:
    SCHEMA = yaml.load(schema_file, yaml.Loader)

# Creates two lists to store QR codes separated into objective and subjective
QR_OBJ = []
QR_SUBJ = []

# Reads competition.txt file, which only contains the competition code, in order to find the
# competition document
with open('data/competition.txt') as file:
    COMPETITION_CODE = file.read()

# Acquires the raw data from competition document
DB = MongoClient('localhost', 27017).scouting_system
RAW_DATA = DB.competitions.find_one({'tba_event_code': COMPETITION_CODE})['raw']

# Appends individual QR codes to QR_CODES
# Checks the schema document for the starting character of subjective and objective QR codes, and
# splits the QR codes into objective and subjective QR codes at the same time, if the QR code isn't
# already the already split list, or already in the database it doesn't add it
for qr_code in QR_DATA:
    if qr_code.startswith(SCHEMA['subjective']['_start_character']):
        if qr_code not in QR_SUBJ and qr_code not in RAW_DATA['qr_subj']:
            QR_SUBJ.append(qr_code)
        else:
            print(f'Removed a duplicate subjective QR code: {qr_code}')
    elif qr_code.startswith(SCHEMA['objective_tim']['_start_character']):
        if qr_code not in QR_OBJ and qr_code not in RAW_DATA['qr_obj']:
            QR_OBJ.append(qr_code)
        else:
            print(f'Removed a duplicate objective QR code: {qr_code}')
    else:
        raise ValueError('QR Code does not have a valid start character')

# Adds the objective and subjective QR codes to the local database if the lists aren't empty
if QR_OBJ != []:
    DB.competitions.update_one({'tba_event_code': COMPETITION_CODE},
                               {'$push': {'raw.qr_obj': {'$each': QR_OBJ}}})
if QR_SUBJ != []:
    DB.competitions.update_one({'tba_event_code': COMPETITION_CODE},
                               {'$push': {'raw.qr_subj': {'$each': QR_SUBJ}}})

remove('data/qr_input.txt')
