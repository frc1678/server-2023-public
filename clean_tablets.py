#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Changes font size of tablets for app consistency"""
# External imports
import time
# Internal imports
import utils

def adb_font_size_enforcer(font_size):
    # Stores output from 'adb devices'
    # 'adb devices' returns the serial numbers of all devices connected over ADB.
    # Example output of 'adb devices':
    # "List of devices attached\nHA0XUZA9\tdevice\n9AMAY1E53P\tdevice"
    output = utils.run_command('adb devices', return_output=True)
    # [1:] removes 'List of devices attached'
    output = output.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    devices = [line.split('\t')[0] for line in output]
    # Wait for USB connection to initialize
    time.sleep(.1)
    for device in devices:
        # The -s flag specifies the device by its serial number.
        utils.run_command(
            f'adb -s {device} shell settings put system font_scale {font_size}',
            return_output=False
        )

