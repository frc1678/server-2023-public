#!/usr/bin/python3.6
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Takes user input for QR codes from QR scanner and sends them to local database

QR scanner 'Endmarke' setting must be set to tabs
"""
# No external imports
# Internal imports
import qr_code_uploader

# Takes user input from QR scanner
QR_DATA = input('Scan data here: ')

# If the user input is nothing, nothing gets added to the database
if QR_DATA == '':
    raise ValueError('There is no data entered')

# '\t' refers to tab character; rstrip removes trailing tab from end mark of last QR code
QR_DATA = QR_DATA.rstrip('\t').split('\t')

# Uploads QR codes to database
qr_code_uploader.upload_qr_codes(QR_DATA)
