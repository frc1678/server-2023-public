#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Create match schedule and team list files and send them to devices.

Retrieve match schedule from TBA. Create team list from match schedule, send match schedule file to
scout tablets over ADB, and verify that the file is successfully transferred. ADB stands for
Android Debug Bridge.
"""

import csv
import hashlib
import json
import time

from data_transfer import adb_communicator, tba_communicator
import utils


def create_match_schedule_csv(local_file_path, tba_request_url):
    """Creates a CSV file based on database's cached matches.

    Parameters: local_file_path (string): path to match_schedule.csv
    tba_request_url: api_url for calling tba_communicator.tba_request()
    :returns None on success, 1 on failure.
    """
    # Get matches from database
    matches = tba_communicator.tba_request(tba_request_url)
    # Don't try to create match schedule if matches returns a blank list
    if matches == []:
        return 1
    # Filter out elimination matches; we don't use them for scouting
    matches = [match for match in matches if match['comp_level'] == 'qm']
    with open(local_file_path, 'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the match key and teams to the CSV file row by row,
        # but using a slightly different format from what's on the tba_cache of the database.
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
        utils.log_info(f'Match schedule created at {local_file_path}, url is {tba_request_url}')


def get_team_list():
    """Returns team list from match schedule file."""
    teams = set()
    if not SEND_MATCH_SCHEDULE:
        teams = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/teams/simple')
        # TBA returns a dictionary of information about teams at the event, so extract team numbers
        team_numbers = [team['team_number'] for team in teams]
        return sorted(team_numbers)
    # Create stream from local match schedule copy to prevent extra handling for csv.reader
    with open(MATCH_SCHEDULE_LOCAL_PATH) as file:
        # Create csv reader from match schedule
        match_schedule_reader = csv.reader(file)
        for match in match_schedule_reader:
            # Filter match number from match schedule list
            for team in match[1:]:
                # Strip alliance color information from team number before adding it
                teams.add(team[2:])
    # Return a list of teams sorted by team number
    return sorted(map(int, teams))


def write_team_list(output_file_path):
    """Writes team list to file."""
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
    tablet_data = adb_communicator.get_tablet_file_path_hash(device_id, tablet_file_path)
    if local_file_path == MATCH_SCHEDULE_LOCAL_PATH:
        return tablet_data == LOCAL_MATCH_SCHEDULE_HASH
    if local_file_path == TEAM_LIST_LOCAL_PATH:
        return tablet_data == LOCAL_TEAM_LIST_HASH
    raise ValueError(f'File path {local_file_path} not recognized.')


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
if (
    create_match_schedule_csv(
        MATCH_SCHEDULE_LOCAL_PATH, f'event/{utils.TBA_EVENT_KEY}/matches/simple'
    )
    == 1
):
    SEND_MATCH_SCHEDULE = False
else:
    SEND_MATCH_SCHEDULE = True

# LOCAL_MATCH_SCHEDULE contains the text of the match_schedule.csv file, which we compare with the
# output of cat (run on tablets through adb shell) for file validations.
if SEND_MATCH_SCHEDULE:
    with open(MATCH_SCHEDULE_LOCAL_PATH, 'rb') as match_schedule_file:
        # Store sha256 sum of match schedule
        LOCAL_MATCH_SCHEDULE_HASH = hashlib.sha256(match_schedule_file.read()).hexdigest()
# Team list must be created after local match schedule copy is loaded
write_team_list(TEAM_LIST_LOCAL_PATH)
with open(TEAM_LIST_LOCAL_PATH, 'rb') as team_list_file:
    # Store sha256 sum of team list
    LOCAL_TEAM_LIST_HASH = hashlib.sha256(team_list_file.read()).hexdigest()

# Only upload schedules if file is ran, not imported
if __name__ == '__main__':
    # List of devices to which 'match_schedule.csv' has already been sent
    DEVICES_WITH_SCHEDULE, DEVICES_WITH_LIST = set(), set()
    DEVICES = set(adb_communicator.get_attached_devices())

    print(f'Attempting to send:\n"{TEAM_LIST_LOCAL_PATH}"')
    if SEND_MATCH_SCHEDULE:
        print(f'{MATCH_SCHEDULE_LOCAL_PATH}"\n')
    else:
        print(f'Match Schedule for "{utils.TBA_EVENT_KEY}" not available')

    while True:
        # Wait for USB connection to initialize
        time.sleep(0.1)
        for device in DEVICES:
            device_name = adb_communicator.DEVICE_SERIAL_NUMBERS[device]
            if device not in DEVICES_WITH_SCHEDULE and SEND_MATCH_SCHEDULE:
                print(f'\nAttempting to load {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}')
                if adb_communicator.push_file(
                    device, MATCH_SCHEDULE_LOCAL_PATH, MATCH_SCHEDULE_TABLET_PATH, validate_file
                ):
                    DEVICES_WITH_SCHEDULE.add(device)
                    print(f'Loaded {MATCH_SCHEDULE_LOCAL_PATH} onto {device_name}')
                else:
                    # Give both serial number and device name in warning
                    utils.log_warning(
                        f'FAILED sending {MATCH_SCHEDULE_LOCAL_PATH} to {device_name} ({device})'
                    )
            if device not in DEVICES_WITH_LIST:
                print(f'\nAttempting to load {TEAM_LIST_LOCAL_PATH} onto {device_name}')
                if adb_communicator.push_file(
                    device, TEAM_LIST_LOCAL_PATH, TEAM_LIST_TABLET_PATH, validate_file
                ):
                    DEVICES_WITH_LIST.add(device)
                    print(f'Loaded {TEAM_LIST_LOCAL_PATH} to {device_name}')
                else:
                    # Give both serial number and device name in warning
                    utils.log_warning(
                        f'FAILED sending {TEAM_LIST_LOCAL_PATH} to {device_name} ({device})'
                    )
        # Update connected devices before checking if program should exit
        DEVICES = set(adb_communicator.get_attached_devices())
        if DEVICES == DEVICES_WITH_SCHEDULE and DEVICES == DEVICES_WITH_LIST:
            # Print blank lines for visual distinction
            print('\n')
            # Schedule has been loaded onto all connected devices
            if SEND_MATCH_SCHEDULE:
                if len(DEVICES_WITH_SCHEDULE) != 1:
                    print(f'Match schedule loaded onto {len(DEVICES_WITH_SCHEDULE)} devices.')
                else:
                    print('Match schedule loaded onto 1 device.')
            if len(DEVICES_WITH_LIST) != 1:
                print(f'Team list loaded onto {len(DEVICES_WITH_LIST)} devices.')
            else:
                print('Team list loaded onto 1 device.')
            break
