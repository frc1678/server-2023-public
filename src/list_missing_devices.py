#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Elegantly displays attached and missing devices."""

from termcolor import colored

from data_transfer import adb_communicator


def missing_devices():
    """Loops through device serials and checks if the device is connected

    prints in color based on missing status.
    """
    print(colored('Normally Pixel 3a #1-3 and Lenovo Tab E7 #1-28 should be here.', 'yellow'))
    print(
        'Lenovo Tab E7 #29-33 are not included in the tablet cases unless tablets have been switched out.'
    )
    devices = adb_communicator.get_attached_devices()
    # Gets all devices
    for device in adb_communicator.DEVICE_SERIAL_NUMBERS:
        # Checks if device is connected
        if device not in devices:
            print(colored(adb_communicator.DEVICE_SERIAL_NUMBERS[device], 'red'))
        else:
            print(colored(adb_communicator.DEVICE_SERIAL_NUMBERS[device], 'green'))


missing_devices()
