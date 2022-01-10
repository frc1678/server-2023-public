#!/usr/bin/env python3
# Copyright (c) 2019-2021 FRC Team 1678: Citrus Circuits
"""Changes font size of tablets for app consistency."""

from data_transfer import adb_communicator
import os
import utils
import shutil


class TabletClean:
    """Enforce settings and clean unneeded local data copied over from tablets"""

    def __init__(self, tablet_data_path="data/tablets"):
        """Set default settings for tablet data path and default font size

        Both of the values have defaults and can be overwritten by parameters.
        This is to have the default settings run without change in this script
        but also have the ability to be run by other files with deferent
        defaults"""
        self.tablet_data_path = tablet_data_path

    def clean_local_tablet_directory(self):
        """Clean out files in data/tablets"""
        # Checks if the directory exists
        if os.path.isdir(self.tablet_data_path):
            # Deletes the directory
            print("Deleting all files in {self.tablet_data_path}")
            shutil.rmtree(self.tablet_data_path)
        # Creates the tablet directory again
        utils.create_file_path(self.tablet_data_path, True)


if __name__ == "__main__":
    FILE_PATH = utils.create_file_path("data/tablets")
    adb_communicator.adb_font_size_enforcer()

    # Checks if the server operator wants to delete tablet data
    delete_tablet_data = input("Delete all local tablet data: [y/N] ")
    if delete_tablet_data.upper() == "Y":
        clean_tablets = TabletClean()
        # Deletes tablet data from local tablet directory
        clean_tablets.clean_local_tablet_directory()
