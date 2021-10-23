#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Create match schedule and team list files and send them to devices.

Retrieve match schedule from TBA. Create team list from match schedule, send match schedule file to
scout tablets over ADB, and verify that the file is successfully transferred. ADB stands for
Android Debug Bridge.
"""

import argparse
import csv
import hashlib
import time
from typing import List
from dataclasses import dataclass

from data_transfer import adb_communicator, tba_communicator
import utils
from server import Server


@dataclass
class LocalAndTabletPath:
    local: str
    tablet: str

    def __repr__(self):
        return f"LocalAndTabletPath(local={self.local}, \
            tablet={self.tablet})"


class MatchListGenerator:
    def __init__(self, tba_request_url: str):
        """Creates a CSV file based on database's cached matches.

        Parameters: tba_request_url: api_url for calling tba_communicator.tba_request()
        """
        self.tba_request_url = tba_request_url

        # Generate the data, save it as a list
        self.match_schedule_file_data: List[str] = self.create_match_schedule_csv()
        self.success = self.check()

    def create_match_schedule_csv(self) -> List[str]:
        """Get the data from tba_request and generate the match_schedule data"""
        # Get matches from database
        matches = tba_communicator.tba_request(self.tba_request_url)
        # Don't try to create match schedule if matches returns a blank list
        if matches == []:
            raise "No matches on tba"
        # Filter out elimination matches; we don't use them for scouting
        matches = [match for match in matches if match['comp_level'] == 'qm']

        # Make local list to append to
        local_match_schedule_file_data: List[str] = []

        # Generate a match schedule line by line, and add it to a list
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
            local_match_schedule_file_data.append(new_row)
        return local_match_schedule_file_data

    def check(self):
        """Check if the data was created correctly"""
        checks = 0
        if isinstance(self.match_schedule_file_data, list):
            checks += 1
        if len(self.match_schedule_file_data) > 0:
            checks += 1
        if checks >= 2:
            return True
        else:
            return False

    def return_match_schedule_data(self) -> List[str]:
        """Get the match schedule as a list in case writing is not needed"""
        return self.match_schedule_file_data

    def write(self, local_file_path: str):
        """Write the list of matches to a file"""
        with open(local_file_path, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for match in self.match_schedule_file_data:
                csv_writer.writerow(match)
        print("Match schedule written!")


class TeamListGenerator:
    def __init__(self, match_schedule_local_path: str, send_match_schedule: bool):
        self.send_match_schedule = send_match_schedule
        self.team_list = self.get_team_list()
        self.match_schedule_local_path = match_schedule_local_path

    def get_team_list(self) -> List:
        """Returns team list from match schedule file."""
        teams = set()
        if not self.send_match_schedule:
            teams = tba_communicator.tba_request(f'event/{Server.TBA_EVENT_KEY}/teams/simple')
            # TBA returns a dictionary of information about teams at the event, so extract team numbers
            team_numbers = [team['team_number'] for team in teams]
            return sorted(team_numbers)
        # Create stream from local match schedule copy to prevent extra handling for csv.reader
        with open(self.match_schedule_local_path, "r") as file:
            # Create csv reader from match schedule
            match_schedule_reader = csv.reader(file)
            for match in match_schedule_reader:
                # Filter match number from match schedule list
                for team in match[1:]:
                    # Strip alliance color information from team number before adding it
                    teams.add(team[2:])
        # Return a list of teams sorted by team number
        return sorted(map(int, teams))

    def check(self):
        """Check if the data was created correctly"""
        checks = 0
        if isinstance(self.team_list, set):
            checks += 1
        if len(self.team_list) > 0:
            checks += 1
        if checks >= 2:
            return True
        else:
            return False

    def write(self, output_file_path: str):
        """Writes team list to file."""
        team_list = self.get_team_list()
        with open(output_file_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(team_list)


def validate_file(
    device_id: str,
    local_file_path: str,
    tablet_file_path: str,
    local_match_schedule_hash: str,
    local_team_list_hash: str,
):
    """Validates that `local_file_path` file was successfully transferred.

    Compares the `tablet_file_path` on the tablet to the locally stored
    version of the same file.

    Parameter 'device_id' is the serial number of the device
    """
    tablet_data = adb_communicator.get_tablet_file_path_hash(device_id, tablet_file_path)
    if local_file_path == match_schedule_local_path:
        return tablet_data == local_match_schedule_hash
    if local_file_path == team_list_local_path:
        return tablet_data == local_team_list_hash
    raise ValueError(f'File path {local_file_path} not recognized.')


class Sender:
    def __init__(
        self, match_schedule_paths: LocalAndTabletPath, team_list_paths: LocalAndTabletPath
    ):

        # Setup paths
        self.team_list_local_path = team_list_paths.local
        self.team_list_tablet_path = team_list_paths.tablet

        self.match_schedule_local_path = match_schedule_paths.local
        self.match_schedule_tablet_path = match_schedule_paths.tablet

        self.devices_with_schedule = set()
        self.devices_with_list = set()

        self.devices = set(adb_communicator.get_attached_devices())

    def confirm_prep_and_generation(self):
        print(f'You are working with the competition {Server.TBA_EVENT_KEY}.')

        # Match schedule must be created before local copy is loaded
        match_list_generator = MatchListGenerator(f'event/{Server.TBA_EVENT_KEY}/matches/simple')
        if match_list_generator.success:
            self.send_match_schedule = False
        else:
            self.send_match_schedule = True

        match_list_generator.write(self.match_schedule_local_path)

        team_list_generator = TeamListGenerator(
            self.match_schedule_local_path, self.send_match_schedule
        )

        team_list_generator.write(self.team_list_local_path)

        # LOCAL_MATCH_SCHEDULE contains the text of the match_schedule.csv file, which we compare with the
        # output of cat (run on tablets through adb shell) for file validations.
        if self.send_match_schedule:
            with open(self.match_schedule_local_path, 'rb') as match_schedule_file:
                # Store sha256 sum of match schedule
                local_match_schedule_hash = hashlib.sha256(match_schedule_file.read()).hexdigest()
        # Team list must be created after local match schedule copy is loaded
        team_list_generator.write(self.team_list_local_path)
        with open(self.team_list_local_path, 'rb') as team_list_file:
            # Store sha256 sum of team list
            local_team_list_hash = hashlib.sha256(team_list_file.read()).hexdigest()

    def send(self):
        print(f'Attempting to send:\n"{self.team_list_local_path}"')
        if self.send_match_schedule:
            print(f'{self.match_schedule_local_path}"\n')
        else:
            print(f'Match Schedule for "{Server.TBA_EVENT_KEY}" not available')

        while True:
            # Wait for USB connection to initialize
            time.sleep(0.1)
            for device in self.devices:
                device_name = adb_communicator.DEVICE_SERIAL_NUMBERS[device]
                if device not in self.devices_with_schedule and self.send_match_schedule:
                    print(
                        f'\nAttempting to load {self.match_schedule_local_path} onto {device_name}'
                    )
                    if adb_communicator.push_file(
                        device,
                        self.match_schedule_local_path,
                        self.match_schedule_tablet_path,
                        validate_file,
                    ):
                        self.devices_with_schedule.add(device)
                        print(f'Loaded {self.match_schedule_local_path} onto {device_name}')
                    else:
                        # Give both serial number and device name in warning
                        utils.log_warning(
                            f'FAILED sending {self.match_schedule_local_path} to {device_name} ({device})'
                        )
                if device not in self.devices_with_list:
                    print(f'\nAttempting to load {self.team_list_local_path} onto {device_name}')
                    if adb_communicator.push_file(
                        device, self.team_list_local_path, self.team_list_tablet_path, validate_file
                    ):
                        self.devices_with_list.add(device)
                        print(f'Loaded {self.team_list_local_path} to {device_name}')
                    else:
                        # Give both serial number and device name in warning
                        utils.log_warning(
                            f'FAILED sending {self.team_list_local_path} to {device_name} ({device})'
                        )
            # Update connected devices before checking if program should exit
            self.devices = set(adb_communicator.get_attached_devices())
            if (
                self.devices == self.devices_with_schedule
                and self.devices == self.devices_with_list
            ):
                # Print blank lines for visual distinction
                print('\n')
                # Schedule has been loaded onto all connected devices
                if self.send_match_schedule:
                    if len(self.devices_with_schedule) != 1:
                        print(
                            f'Match schedule loaded onto {len(self.devices_with_schedule)} devices.'
                        )
                    else:
                        print('Match schedule loaded onto 1 device.')
                if len(self.devices_with_list) != 1:
                    print(f'Team list loaded onto {len(self.devices_with_list)} devices.')
                else:
                    print('Team list loaded onto 1 device.')
                    break


def argument_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument("-g", action='store_true', help="Generate match_schedule and team_list only")
    parse.add_argument(
        "-s", action='store_true', help="Generate and Send match_schedule and team_list"
    )
    return parse.parse_args()


if __name__ == '__main__':
    # Set paths to read from and write to
    match_schedule_tablet_path = '/storage/self/primary/Download/match_schedule.csv'
    match_schedule_local_path = utils.create_file_path('data/match_schedule.csv')
    team_list_tablet_path = '/storage/self/primary/Download/team_list.csv'
    team_list_local_path = utils.create_file_path('data/team_list.csv')

    # Make paths object
    match_schedule_paths = LocalAndTabletPath(match_schedule_local_path, match_schedule_tablet_path)
    team_list_paths = LocalAndTabletPath(team_list_local_path, team_list_tablet_path)

    # Send the files over
    sender = Sender(match_schedule_paths, team_list_paths)

    args = argument_parser()

    if args.g:
        sender.confirm_prep_and_generation()
    elif args.s:
        sender.confirm_prep_and_generation()
        sender.send()
    else:
        print("Run send_match_schedule.py --help")
