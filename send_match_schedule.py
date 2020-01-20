#!/usr/bin/python3.6
"""Create match schedule and send it to devices.

Retrieve match schedule from TBA,
send match schedule file to scout tablets over ADB,
and verify that the file is successfully transferred.
ADB stands for Android Debug Bridge."""

# External imports
import csv
import json
import subprocess
import time
# Internal imports
import tba_communicator
import utils

def create_match_schedule_csv(local_file_path, tba_request_url):
    """Creates a CSV file based on database's cached matches

    Parameters: local_file_path (string): path to match_schedule.csv
    tba_request_url: api_url for calling tba_communicator.tba_request()"""
    # Get matches from database
    matches = tba_communicator.tba_request(tba_request_url)
    # Filter out elimination matches; we don't use them for scouting
    matches = [match for match in matches if match['comp_level'] == 'qm']
    with open(local_file_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the match key and teams to the CSV file row by row,
        # but using a slightly different format from what's on the tba_cache of the database
        for match in matches:
            # match['key'] has event code, and underscore, then the match
            # example: '2019carv_qm118'
            match_key = match['key'].split('_qm')[1]
            # Each row contains the match, the blue teams, and the red teams
            # Example: 69,B-4911,B-4290,B-2662,R-2375,R-6390,R-3792
            new_row = [match_key]
            for alliance in ['blue', 'red']:
                teams = match['alliances'][alliance]['team_keys']
                if alliance == 'blue':
                    team_prefix = 'B-'
                else:
                    team_prefix = 'R-'
                teams = [team_prefix + team.split('frc')[1] for team in teams]
                new_row += teams
            csv_writer.writerow(new_row)


def validate_file(device_id):
    """Validates that the match schedule file was successfully transferred.

    Compares the match_schedule.csv on the tablet to the locally stored
    version of the same file.

    Parameter 'device_id' is the serial number of the device"""
    # Reads the match_schedule.csv file on the tablet
    # The -s flag specifies a device by its serial number
    tablet_data = run_command(f'adb -s {device_id} shell cat {TABLET_FILE_PATH}',
                              return_output=True)
    return tablet_data == LOCAL_COPY

def run_command(command, return_output=False):
    """Runs a command using subprocess.

    command (string) is the terminal command to be run
    returns the standard output of the command if return_output is True"""
    # We use .split(' ') because subprocess.run() expects the command as a list of strings
    # Example, .run(['echo', 'hello']) instead of .run('echo hello')
    command = command.split(' ')
    if return_output is True:
        output = subprocess.run(command, check=True, stdout=subprocess.PIPE).stdout
        # output is a byte-like string and needs to be decoded
        # Replace '\r\n' with '\n' to match the UNIX format for newlines
        # Remove trailing newlines
        output = output.decode('utf-8').replace('\r\n', '\n').rstrip('\n')
        return output
    subprocess.run(command, check=True)
    return None

print(f'You are working with the competition {tba_communicator.EVENT_CODE}. Is that right?')
while True:
    if input('Hit enter to continue, or Ctrl-C to exit:') == '':
        break

# Serial number to human-readable device name
# Tablet serials are stored in a file not tracked by git
with open(utils.create_file_path('data/tablet_serials.json')) as file:
    DEVICE_NAMES = json.load(file)

TABLET_FILE_PATH = '/storage/self/primary/Download/match_schedule.csv'
LOCAL_FILE_PATH = utils.create_file_path('data/match_schedule.csv')

create_match_schedule_csv(LOCAL_FILE_PATH, f'event/{tba_communicator.EVENT_CODE}/matches/simple')

# LOCAL_COPY contains the text of the match_schedule.csv file, which we compare with the output of
# cat (run on tablets through adb shell) for file validations
with open(LOCAL_FILE_PATH, 'r') as file:
    LOCAL_COPY = file.read().rstrip('\n')

# List of devices to which 'match_schedule.csv' has already been sent
DEVICES_WITH_FILE = []

print(f'Attempting to send file "{LOCAL_FILE_PATH}". Please plug devices into computer to begin.')
while True:
    # Stores output from 'adb devices'
    # 'adb devices' returns the serial numbers of all devices connected over ADB.
    # Example output of 'adb devices':
    # "List of devices attached\nHA0XUZA9\tdevice\n9AMAY1E53P\tdevice"
    OUTPUT = run_command('adb devices', return_output=True)
    # [1:] removes 'List of devices attached'
    OUTPUT = OUTPUT.rstrip('\n').split('\n')[1:]
    # Remove '\tdevice' from each line
    DEVICES = [line.split('\t')[0] for line in OUTPUT]

    # Wait for USB connection to initialize
    time.sleep(.1)  # .1 seconds

    for device in DEVICES:
        if device not in DEVICES_WITH_FILE:
            # Calls 'adb push' command, which uses the Android Debug
            # Bridge (ADB) to copy the match schedule file to the tablet.
            # The -s flag specifies the device by its serial number.
            run_command(f'adb -s {device} push {LOCAL_FILE_PATH} {TABLET_FILE_PATH}')

            if validate_file(device) is True:
                DEVICES_WITH_FILE.append(device)
                # Convert serial number to human-readable name
                device_name = DEVICE_NAMES[device]
                print(f'Loaded {LOCAL_FILE_PATH} onto {device_name}')
