#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Standardizes tablet font size, deletes old data, and uninstalls apps."""

from data_transfer import adb_communicator
import os
import utils
import shutil


class TabletClean:
    """Clean local data copied over from tablets"""

    def __init__(self, tablet_data_path='data/devices'):
        """Set default settings for tablet data path and default font size

        Both of the values have defaults and can be overwritten by parameters.
        This is to have the default settings run without change in this script
        but also have the ability to be run by other files with deferent
        defaults"""
        self.tablet_data_path = tablet_data_path

    def clean_local_tablet_directory(self):
        """Cleans out files in the data/devices directory on the server computer."""
        # Checks if the directory exists
        if os.path.isdir(self.tablet_data_path):
            # Deletes the directory
            shutil.rmtree(self.tablet_data_path)
            utils.log_info(f'Deleted all files in {self.tablet_data_path}')
        # Creates the tablet directory again
        utils.create_file_path(self.tablet_data_path, True)


if __name__ == '__main__':
    FILE_PATH = utils.create_file_path('data/devices')
    DEVICES = adb_communicator.get_attached_devices()

    adb_communicator.adb_font_size_enforcer()
    print('Enforced tablet font size')

    # Checks if the server operator wants to delete tablet data
    delete_tablet_data = input('Delete all local tablet data: [y/N]')
    if delete_tablet_data.upper() == 'Y':
        clean_tablets = TabletClean()
        # Deletes tablet data from local tablet directory
        clean_tablets.clean_local_tablet_directory()
        print(f'Deleted all files in {clean_tablets.tablet_data_path}')

    delete_tablet_downloads = input(
        'Delete all tablet downloads (includes match schedule and teams list files and downloaded QRs): [y/N]'
    )
    if delete_tablet_downloads.upper() == 'Y':
        adb_communicator.delete_tablet_downloads()
        print('Deleted all downloaded files from tablets.')

    uninstall_match_collection = input('Uninstall match collection from tablets: [y/N]')
    if uninstall_match_collection.upper() == 'Y':
        for device in DEVICES:
            adb_communicator.uninstall_app(device)
            print(
                f'Uninstalled Match Collection from {adb_communicator.DEVICE_SERIAL_NUMBERS[device]}'
            )
