#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Send APK file to tablets over ADB.

Uses subprocess to send an APK to the tablets.
ADB stands for Android Debug Bridge.
"""
# External imports
import json
import sys
import time
# Internal imports
import adb_communicator
import utils


def install_apk(device_serial):
    """Installs chosen APK to either phone or tablet depending on user input.

    Convert serial number to human-readable format.
    """
    device_name = adb_communicator.DEVICE_SERIAL_NUMBERS[device_serial]
    print(f'Loading {LOCAL_FILE_PATH} onto {device_name}')
    # Calls 'adb push' command, which uses the Android Debug Bridge (ADB) to send the APK file
    # The -s flag specifies the device_serial by its serial number
    # return_output=True returns the output of adb
    utils.log_info(f'APK install started on {device_serial}')
    validate = utils.run_command(
        f'adb -s {device_serial} install -r {LOCAL_FILE_PATH}', return_output=True)
    # If .apk is loaded successfully, ADB will output a string containing 'Success'
    if 'Success' in validate:
        DEVICES_WITH_APK.append(device_serial)
        print(f'Loaded {LOCAL_FILE_PATH} onto {device_name}')
        utils.log_info(f'APK successefully installed on {device_serial}')
    else:
        utils.log_warning(f'Failed Loading {LOCAL_FILE_PATH} onto {device_name}.')


if len(sys.argv) == 2:
    # Extract LOCAL_FILE_PATH from second argument
    # LOCAL_FILE_PATH is a string
    LOCAL_FILE_PATH = sys.argv[1]
else:
    print('Error: Local APK file path is not being passed as an argument. Exiting...')
    sys.exit(1)

# List of devices to which the apk has already been sent
DEVICES_WITH_APK = []

# Phones and Tablets use different APKs
# This specifies which type of device_serial it will be sent to so it will not send to both
CHOSEN_DEVICE = input('Would you like the apk to be sent to Tablet or Phone?(t/p) ').lower()
if CHOSEN_DEVICE == 't':
    CHOSEN_DEVICE_VALUE = 'tablet'
elif CHOSEN_DEVICE == 'p':
    CHOSEN_DEVICE_VALUE = 'phone'
else:
    print('Error: (t)ablet or (p)hone not specified.')
    sys.exit(1)

print(f'Attempting to send file "{LOCAL_FILE_PATH}".')

while True:
    DEVICES = adb_communicator.get_attached_devices()
    TABLET_SERIALS, PHONE_SERIALS = [], []

    # Determine if each connected device_serial is a tablet or phone and if it needs the APK
    for serial in DEVICES:
        if serial.split('A')[0] == 'H':
            # Only add device_serial if it does not already have the apk
            if serial not in DEVICES_WITH_APK:
                TABLET_SERIALS.append(serial)
        if serial.split('A')[0] == '9':
            # Only add device_serial if it does not already have the apk
            if serial not in DEVICES_WITH_APK:
                PHONE_SERIALS.append(serial)

    # Wait for USB connection to initialize
    time.sleep(.1) #  .1 seconds
    if CHOSEN_DEVICE == 't':
        # APK has been installed onto all connected tablets
        if TABLET_SERIALS == []:
            break
        for device in TABLET_SERIALS:
            install_apk(device)
    if CHOSEN_DEVICE == 'p':
        # APK has been installed onto all connected phones
        if PHONE_SERIALS == []:
            break
        for device in PHONE_SERIALS:
            install_apk(device)
