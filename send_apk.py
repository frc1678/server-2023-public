#!/usr/bin/python3.6
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Send APK file to tablets over ADB.

Uses subprocess to send an APK to the tablets
ADB stands for Android Debug Bridge."""

# External imports
import json
import sys
import time
# Internal imports
import utils


if len(sys.argv) == 2:
    # Extract LOCAL_FILE_PATH from second argument
    # LOCAL_FILE_PATH is a string
    LOCAL_FILE_PATH = sys.argv[1]
else:
    print('Error: Local APK file path is not being passed as an argument. Exiting...')
    sys.exit(0)


def install_apk():
    """Installs chosen APK to either phone or tablet depending on user input."""
    if device not in DEVICES_WITH_APK:
        # Calls 'adb push' command, which uses the Android Debug
        # Bridge (ADB) to send the APK file to the tablet.
        # The -s flag specifies the device by its serial number.
        # return_output=True mutes the 'success' usually returned by this command
        validate = utils.run_command(
            f'adb -s {device} install -r {LOCAL_FILE_PATH}', return_output=True)
        if validate == 'Success':
            DEVICES_WITH_APK.append(device)
            # Convert serial number to human-readable name
            device_name = DEVICE_NAMES[device]
            print(f'Loaded {LOCAL_FILE_PATH} onto {device_name}')


# Gets the tablet serial numbers from a local file
with open(utils.create_file_path('data/tablet_serials.json')) as file:
    DEVICE_NAMES = json.load(file)

# List of devices to which the apk has already been sent
DEVICES_WITH_APK = []

# Phones and Tablets use different APKs
# This specifies which type of device it will be sent to so it will not send to both
CHOSEN_DEVICE = input('Would you like the apk to be sent to Tablet or Phone?(t/p) ')
TABLET_SERIALS = []
PHONE_SERIALS = []
if CHOSEN_DEVICE.lower() == 't':
    CHOSEN_DEVICE_VALUE = 'tablet'
if CHOSEN_DEVICE.lower() == 'p':
    CHOSEN_DEVICE_VALUE = 'phone'
print(f'Attempting to send file "{LOCAL_FILE_PATH}". Please plug '
      f'{CHOSEN_DEVICE_VALUE}s into computer to begin.')
while True:
    # Stores output from 'adb devices'
    # 'adb devices' returns the serial numbers of all devices connected over ADB.
    # Example output of 'adb devices':
    # "List of devices attached\nHA0XUZA9\tdevice\n9AMAY1E53P\tdevice"
    OUTPUT = utils.run_command('adb devices', return_output=True)
    # [1:] removes 'List of devices attached'
    OUTPUT = OUTPUT.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    DEVICES = [line.split('\t')[0] for line in OUTPUT]
    for serial in DEVICES:
        if serial.split('A')[0] == 'H':
            TABLET_SERIALS.append(serial)
        if serial.split('A')[0] == '9':
            PHONE_SERIALS.append(serial)
    # Wait for USB connection to initialize
    time.sleep(.1)  # .1 seconds

    if CHOSEN_DEVICE.lower() == 't':
        for device in TABLET_SERIALS:
            install_apk()
    if CHOSEN_DEVICE.lower() == 'p':
        for device in PHONE_SERIALS:
            install_apk()
