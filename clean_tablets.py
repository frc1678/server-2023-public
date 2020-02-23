#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Changes font size of tablets for app consistency"""
# External imports
import time
# Internal imports
import adb_communicator
import utils


def adb_font_size_enforcer():
    """Enforce tablet font size to 1.30, the largest supported size"""
    devices = adb_communicator.get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(.1)
    for device in devices:
        # The -s flag specifies the device by its serial number.
        utils.run_command(
            f'adb -s {device} shell settings put system font_scale 1.30',
            return_output=False
        )


file_path = utils.create_file_path('data/tablets')
utils.run_command(f'rm -R {file_path}', True)
utils.run_command('mkdir data/tablets', True)
adb_font_size_enforcer()
