#!/usr/bin/python3.6
"""Takes user input for QR codes over QR scanner, and runs parse_qr_codes()

Takes user input for QR codes
Removes end tab from QR scanner, and splits user input by tabs for parse_qr_codes.py
QR Scanner 'Endmarke' setting must be set to tabs
"""
# No external imports
# Internal imports
import parse_qr_codes

# Takes user input for the QR data
QR_DATA = input('Scan data here: ')

# If the user input is nothing, nothing gets added to the database
if QR_DATA == '':
    raise ValueError('There is no data entered')

# '\t' refers to tab character, rstrip removes trailing tab from end mark of last QR code
QR_DATA = QR_DATA.rstrip('\t').split('\t')

# Parses the QR codes, see parse_qr_codes.py for more info
parse_qr_codes.parse_qr_codes(QR_DATA)
