#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Create match schedule and team list files and send them to devices.

Retrieve match schedule from TBA,
Create team list from match schedule,
send match schedule file to scout tablets over ADB,
and verify that the file is successfully transferred.
ADB stands for Android Debug Bridge.
"""

# External imports
import csv
import io
import json
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


def get_team_list():
    """Returns team list from match schedule file"""
    teams = set()
    # Create stream from local match schedule copy to prevent extra handling for csv.reader
    match_schedule_stream = io.StringIO(LOCAL_MATCH_SCHEDULE)
    # Create csv reader from match schedule
    match_schedule_reader = csv.reader(match_schedule_stream)
    for match in match_schedule_reader:
        # Filter match number from match schedule list
        for team in match[1:]:
            # Strip alliance color information from team number before adding it
            teams.add(team[2:])
    # Return a list of teams sorted by team number
    return sorted(list(teams), key=int)


def write_team_list(output_file_path):
    """Writes team list to file"""
    team_list = get_team_list()
    with open(output_file_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(team_list)


def validate_file(device_id, local_file_path, tablet_file_path):
    """Validates that `local_file_path` file was successfully transferred.

    Compares the `tablet_file_path` on the tablet to the locally stored
    version of the same file.

    Parameter 'device_id' is the serial number of the device
    """
    # Reads the match_schedule.csv file on the tablet
    # The -s flag specifies a device by its serial number
    tablet_data = utils.run_command(f'adb -s {device_id} shell cat {tablet_file_path}',
                                    return_output=True)
    if local_file_path == MATCH_SCHEDULE_LOCAL_PATH:
        return tablet_data == LOCAL_MATCH_SCHEDULE
    elif local_file_path == TEAM_LIST_LOCAL_PATH:
        return tablet_data == LOCAL_TEAM_LIST
    raise ValueError(f'Filepath {local_file_path} not recognized.')


def push_file(serial_number, local_path, tablet_path):
    """Pushes file at `local_path` to `tablet_path` using ADB. Returns False on failure."""
    # Calls 'adb push' command, which runs over the Android Debug Bridge (ADB) to copy the file at
    # local_path to the tablet
    # The -s flag specifies the device by its serial number.
    push_command = f'adb -s {serial_number} push {local_path} {tablet_path}'
    utils.run_command(push_command)
    # Return bool indicating if file loaded correctly
    return validate_file(serial_number, local_path, tablet_path)


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


# Serial number to human-readable device name
# Tablet serials are stored in a file not tracked by git
with open(utils.create_file_path('data/tablet_serials.json')) as file:
    DEVICE_NAMES = json.load(file)

# Set paths to read from and write to
MATCH_SCHEDULE_TABLET_PATH = '/storage/self/primary/Download/match_schedule.csv'
MATCH_SCHEDULE_LOCAL_PATH = utils.create_file_path('data/match_schedule.csv')
TEAM_LIST_TABLET_PATH = '/storage/self/primary/Download/team_list.csv'
TEAM_LIST_LOCAL_PATH = utils.create_file_path('data/team_list.csv')

print(f'You are working with the competition {utils.TBA_EVENT_KEY}. Is that right?')
while True:
    if input('Hit enter to continue, or Ctrl-C to exit:') == '':
        break

# Match schedule must be created before local copy is loaded
create_match_schedule_csv(MATCH_SCHEDULE_LOCAL_PATH, f'event/{utils.TBA_EVENT_KEY}/matches/simple')
# LOCAL_MATCH_SCHEDULE contains the text of the match_schedule.csv file, which we compare with the
# output of cat (run on tablets through adb shell) for file validations
with open(MATCH_SCHEDULE_LOCAL_PATH, 'r') as file:
    LOCAL_MATCH_SCHEDULE = file.read().rstrip('\n')
# Team list must be created after local match schedule copy is loaded
write_team_list(TEAM_LIST_LOCAL_PATH)
with open(TEAM_LIST_LOCAL_PATH, 'r') as file:
    LOCAL_TEAM_LIST = file.read().rstrip('\n')

# Only upload schedules if file is ran, not imported
if __name__ == '__main__':
    # List of devices to which 'match_schedule.csv' has already been sent
    devices_with_schedule, devices_with_list = [], []
    devices = get_attached_devices()
    pixels = [serial for serial, name in DEVICE_NAMES.items()
              if 'Pixel' in name and serial in devices]

    print(f'Attempting to send:\n"{MATCH_SCHEDULE_LOCAL_PATH}"\n"{TEAM_LIST_LOCAL_PATH}"')

    while True:
        # Wait for USB connection to initialize
        time.sleep(0.1)
        for device in devices:
            device_name = DEVICE_NAMES[device]
            if device not in devices_with_schedule:
                print(f'Attempting to load {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}')
                if push_file(device, MATCH_SCHEDULE_LOCAL_PATH, MATCH_SCHEDULE_TABLET_PATH):
                    devices_with_schedule.append(device)
                    print(f'Loaded {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}')
                else:
                    # Give both serial number and device name in warning
                    utils.log_warning(
                        f'FAILED sending {MATCH_SCHEDULE_LOCAL_PATH} to {device_name} ({device})'
                    )
            if device in pixels and device not in devices_with_list:
                print(f'Attempting to load {TEAM_LIST_LOCAL_PATH} onto {device_name}')
                if push_file(device, TEAM_LIST_LOCAL_PATH, TEAM_LIST_TABLET_PATH):
                    devices_with_list.append(device)
                    print(f'Loaded {TEAM_LIST_LOCAL_PATH} to {device_name}')
                else:
                    # Give both serial number and device name in warning
                    utils.log_warning(
                        f'FAILED sending {TEAM_LIST_LOCAL_PATH} to {device_name} ({device})'
                    )
        # Update connected devices before checking if program should exit
        devices = get_attached_devices()
        pixels = [serial for serial, name in DEVICE_NAMES.items()
                  if 'Pixel' in name and serial in devices]
        if set(devices) == set(devices_with_schedule) and set(pixels) == set(devices_with_list):
            # Schedule has been loaded onto all connected devices
            print(f'Match schedule loaded onto {len(devices_with_schedule)} devices.')
            print(f'Team list loaded onto {len(devices_with_list)} devices.')
            break
