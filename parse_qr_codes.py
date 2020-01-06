#!/usr/bin/python3.6
"""Parse data from QR scanner and upload it to MongoDB.

Data is given as user input using USB keyboard emulation.
QR Scanner 'Endmarke' setting must be set to tabs"""

# '\t' refers to tab character, rstrip removes trailing tab from end mark of last QR code
QR_DATA = input('Scan data here: ').rstrip('\t').split('\t')

# TODO: Upload data to MongoDB
