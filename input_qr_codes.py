#!/usr/bin/python3.6
"""Writes inputted QR codes to a text file to be used in parse_qr_codes.py
Asks what the input method is (Over QR scanner, or USB)
Appends the QR codes to data/qr_input.txt
QR Scanner 'Endmarke' setting must be set to tabs
"""
# No external imports
# No internal imports

# Asks user what method to read the QR codes over
WHERE_TO_READ = input('Enter "0" to input through QR scanner, and "1" to input through USB: ')

# if the user inputs 0, the input method is through the QR scanner, it isn't necessary to parse
# through this input, that is handled in parse_qr_codes.py
if WHERE_TO_READ == '0':
    QR_DATA = input('Scan data here: ')

    if QR_DATA == '':
        raise ValueError('There is no data entered')

    # Writes the QR codes to the qr input text file
    with open('data/qr_input.txt', 'a') as file:
        file.write(QR_DATA)

# TODO: Add QR input over USB

else:
    print('Please enter a valid option for QR input')
