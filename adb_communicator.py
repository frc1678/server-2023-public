#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""adb_compressed_qr_data_puller is a tablet communicator"""
# External imports
import json
import os
import re
import time
# Internal imports
import local_database_communicator
import qr_code_uploader
import utils


def delete_tablet_downloads():
    """Deletes all data from the Download folder of tablets"""
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(.1)
    for device in devices:
        utils.run_command(f'adb -s {device} shell rm -r /storage/sdcard0/Download/*')
        utils.log_info(f'Removed Downloads on {DEVICE_SERIAL_NUMBERS[device]}')


def get_attached_devices():
    """Uses ADB to get a list of devices attached."""
    # Get output from `adb_devices` command. Example output:
    # "List of devices attached\nHA0XUZA9\tdevice\n9AMAY1E53P\tdevice"
    adb_output = utils.run_command('adb devices', return_output=True)
    # Split output by lines
    # [1:] removes line one, 'List of devices attached'
    adb_output = adb_output.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    return [line.split('\t')[0] for line in adb_output]


def push_file(serial_number, local_path, tablet_path, validate_function=None):
    """Pushes file at `local_path` to `tablet_path` using ADB.

    `validate_function` should return a boolean and take a serial number, local_file_path, and
    `tablet_path` in that order
    """
    # Calls 'adb push' command, which runs over the Android Debug Bridge (ADB) to copy the file at
    # local_path to the tablet
    # The -s flag specifies the device by its serial number.
    push_command = f'adb -s {serial_number} push {local_path} {tablet_path}'
    utils.run_command(push_command)
    # Return bool indicating if file loaded correctly
    if validate_function is not None:
        return validate_function(serial_number, local_path, tablet_path)
    return None


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
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(.1)
    # List of devices that have been pulled from (finished)
    devices_finished = []
    for device in devices:
        # Checks if device is finished
        if device not in devices_finished:
            # Creates directory for each tablet in data/
            utils.create_file_path(f'{local_file_path}/{device}')
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the match schedule file to the tablet.
            # The -s flag specifies the device by its serial number.
            utils.run_command(f'adb -s {device} pull {tablet_file_path} {local_file_path}/{device}')


def adb_remove_files(tablet_file_path):
    """This is a function used for removing files on the tablets over ADB

    adb_remove_files finds the list of devices attached then uses the line
    utils.run_command(f'adb -s {device} shell rm -r {tablet_file_path}')
    the adb -s {device} specifies which device to delete from and shell rm -r
    deletes the file from the specified directory that is {tablet_file_path}
    """
    devices = get_attached_devices()
    # Wait for USB connection to initialize
    time.sleep(.1)
    for device in devices:
        # Calls 'adb push' command, which uses the Android Debug
        # Bridge (ADB) to copy the match schedule file to the tablet.
        # The -s flag specifies the device by its serial number.
        utils.run_command(f'adb -s {device} shell rm -r {tablet_file_path}')
        utils.log_info(f'removed {tablet_file_path} on {device}')


def pull_device_data():
    """Pulls tablet data from attached tablets."""
    # Parses 'adb devices' to find num of devices so that don't try to pull from nothing
    devices = get_attached_devices()
    data = {
        'qr': [],
        'obj_pit': [],
        'subj_pit': []
    }
    if not devices:
        return data

    device_file_paths = []
    device_file_path = utils.create_file_path('data/tablets')
    # Pull all files from the 'Download' folder on the tablet
    adb_pull_tablet_data(device_file_path, '/storage/emulated/0/Download')
    # Iterates through the 'data' folder
    for device_dir in os.listdir(device_file_path):
        if device_dir in TABLET_SERIAL_NUMBERS.keys():
            device_file_paths.append(device_dir)
        # If the folder name is a device serial, it must be a tablet folder
    for device in device_file_paths:
        # Iterate through the downloads folder in the device folder
        download_directory = os.path.join(device_file_path, device)
        for file in os.listdir(download_directory):
            for dataset, pattern in FILENAME_REGEXES.items():
                if re.fullmatch(pattern, file):
                    with open(os.path.join(download_directory, file)) as data_file:
                        # QR data is just read
                        if dataset == 'qr':
                            file_contents = data_file.read().rstrip('\n')
                        else:
                            file_contents = json.load(data_file)
                        data[dataset].append(file_contents)
                        break  # Filename will only match one regex
    # Add QRs to database and make sure that only QRs that should be decompressed are added to queue
    data['qr'] = qr_code_uploader.upload_qr_codes(data['qr'])
    for dataset in ['obj_pit', 'subj_pit']:
        current_data = local_database_communicator.read_dataset(dataset)
        modified_data = []
        for datapoint in data[dataset]:
            if datapoint in current_data:
                continue
            # Specify query to ensure that each team only has one entry
            local_database_communicator.append_or_overwrite(
                f'raw.{dataset}', [datapoint], {'team_number': datapoint['team_number']}
            )
            modified_data.append({'team_number': datapoint['team_number']})
        utils.log_info(f'{len(modified_data)} items uploaded to {dataset}')
        data[dataset] = modified_data
    return data


# Store regex patterns to match files containing either pit or match data
FILENAME_REGEXES = {
    # Matches either objective or subjective QR filenames
    # Format of objective QR file pattern: <qual_num>_<team_num>_<serial_num>_<timestamp>.txt
    # Format of subjective QR file pattern: <qual_num>_<serial_num>_<timestamp>.txt
    'qr': re.compile(
        r'([0-9]{1,3}_[0-9]{1,4}_[A-Z0-9]+_[0-9]+\.txt)|([0-9]{1,3}_[0-9A-Z]+_[0-9]+\.txt)'
    ),
    # Format of objective pit file pattern: <team_number>_pit.json
    'obj_pit': re.compile(r'[0-9]{1,4}_obj_pit\.json'),
    # Format of subjective pit file pattern: <team_number>_subjective.json
    'subj_pit': re.compile(r'[0-9]{1,4}_subj_pit\.json')
}

# Open the tablet serials file to find all device serials
with open('data/tablet_serials.json') as serial_numbers:
    DEVICE_SERIAL_NUMBERS = json.load(serial_numbers)
TABLET_SERIAL_NUMBERS = {serial: key for serial, key in DEVICE_SERIAL_NUMBERS.items()
                         if 'Tab' in key}
PHONE_SERIAL_NUMBERS = {serial: key for serial, key in DEVICE_SERIAL_NUMBERS.items()
                        if 'Pixel' in key}
