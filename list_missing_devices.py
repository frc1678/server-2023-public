#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Elegantly displays attached and missing devices"""
# No external imports

# Internal imports
import adb_communicator

def missing_devices():
    """Loops through device serials and checks if the device is connected then prints in color 
    based on missing status."""
    devices = adb_communicator.get_attached_devices()
    # Gets all devices
    for device in adb_communicator.DEVICE_SERIAL_NUMBERS:
        # Checks if device is connected
        if device not in devices:
            print('\033[91m' + adb_communicator.DEVICE_SERIAL_NUMBERS[device]) # Red
        else:
            print('\033[92m' + adb_communicator.DEVICE_SERIAL_NUMBERS[device]) # Green


missing_devices()
