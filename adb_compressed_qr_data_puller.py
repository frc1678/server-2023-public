#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""adb_compressed_qr_data_puller is a tablet communicator"""
# External imports
import time
# Internal imports
import utils


def adb_pull_tablet_data(local_file_path, tablet_file_path):
    """adb_pull_tablet_data is a function for pulling data off tablets

    adb_pull_tablet_data is given a local path and a tablet path.
    It takes the file or directory that is specified as tablet path and
    puts in the directory specified as local path. The directory that is put
    in the local path is a subdirectory of a directory with the name of
    the serial number of the tablet that was pulled from.
    
    Usage:
    adb_pull_tablet_data('/path/to/output/directory', '/path/to/tablet/data')
    """
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
    # List of devices that have been pulled from (finished)
    devices_finished = []
    for device in devices:
        # Checks if device is finished
        if device not in devices_finished:
            # Creates directory for each tablet in data/
            utils.create_file_path(f'data/{device}')
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the match schedule file to the tablet.
            # The -s flag specifies the device by its serial number.
            utils.run_command(f'adb -s {device} pull {tablet_file_path} {local_file_path}{device}')
