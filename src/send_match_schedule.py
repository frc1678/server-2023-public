#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Create match schedule and team list files and send them to devices.

Retrieve match schedule from TBA. Create team list from match schedule, send match schedule file to
scout tablets over ADB, and verify that the file is successfully transferred. ADB stands for
Android Debug Bridge.
"""

import argparse
import time
from typing import List
from dataclasses import dataclass
import json

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
        """Creates a JSON file based on database's cached matches.

        Parameters: tba_request_url: api_url for calling tba_communicator.tba_request()
        """
        self.tba_request_url = tba_request_url
        self.match_schedule_file_data = self.create_match_schedule()

    def get_teams_and_nums(self, match, alliance):
        teams = match["alliances"][alliance]["team_keys"]
        nums = [{"number": int(team.split("frc")[1]), "color": alliance} for team in teams]
        return nums

    def create_match_schedule(self):
        """Get the data from tba_request and generate the match_schedule data"""

        matches = tba_communicator.tba_request(self.tba_request_url)
        if matches == []:
            raise Exception("No matches on tba")

        matches = [match for match in matches if match["comp_level"] == "qm"]
        local_match_schedule_file_data = {}

        for match in matches:
            new = []
            for m in match:
                num = match["key"].split("_qm")[1]

                better_nums = []
                for alliance in ["blue", "red"]:
                    returned = self.get_teams_and_nums(match, alliance)
                    better_nums.extend(returned)

                new.append({"num": num, "teams": better_nums})
            first = new[0]
            local_match_schedule_file_data[first["num"]] = {"teams": first["teams"]}
        return local_match_schedule_file_data

    def return_match_schedule_data(self):
        """Get the match schedule as a list in case writing is not needed"""
        return self.match_schedule_file_data

    def write(self, local_file_path: str):
        """Write the list of matches to a file"""
        with open(local_file_path, "w") as json_file:
            json.dump(self.return_match_schedule_data(), json_file)


class TeamListGenerator:
    def __init__(self, match_schedule_local_path: str, send_match_schedule: bool):
        self.send_match_schedule = send_match_schedule
        self.team_list = self.get_team_list()
        self.match_schedule_local_path = match_schedule_local_path

    def get_team_list(self) -> List:
        """Returns team list from match schedule file."""
        teams = set()

        if not self.send_match_schedule:
            teams = tba_communicator.tba_request(f"event/{Server.TBA_EVENT_KEY}/teams/simple")
            # TBA returns a dictionary of information about teams at the event, so extract team numbers
            team_numbers = [team["team_number"] for team in teams]
            return sorted(team_numbers)

    def write(self, output_file_path: str):
        """Writes team list to file."""
        team_list = self.get_team_list()
        with open(output_file_path, "w") as json_file:
            json.dump(team_list, json_file)


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
    raise ValueError(f"File path {local_file_path} not recognized.")


class Sender:
    def __init__(
        self,
        match_schedule_paths: LocalAndTabletPath,
        team_list_paths: LocalAndTabletPath,
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
        print(f"You are working with the competition {Server.TBA_EVENT_KEY}.")

        # Match schedule must be created before local copy is loaded
        match_list_generator = MatchListGenerator(f"event/{Server.TBA_EVENT_KEY}/matches/simple")
        self.send_match_schedule = False

        match_list_generator.write(self.match_schedule_local_path)

        team_list_generator = TeamListGenerator(
            self.match_schedule_local_path, self.send_match_schedule
        )

        team_list_generator.write(self.team_list_local_path)

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
                        f"\nAttempting to load {self.match_schedule_local_path} onto {device_name}"
                    )
                    if adb_communicator.push_file(
                        device,
                        self.match_schedule_local_path,
                        self.match_schedule_tablet_path,
                        validate_file,
                    ):
                        self.devices_with_schedule.add(device)
                        print(f"Loaded {self.match_schedule_local_path} onto {device_name}")
                    else:
                        # Give both serial number and device name in warning
                        utils.log_warning(
                            f"FAILED sending {self.match_schedule_local_path} to {device_name} ({device})"
                        )
                if device not in self.devices_with_list:
                    print(f"\nAttempting to load {self.team_list_local_path} onto {device_name}")
                    if adb_communicator.push_file(
                        device,
                        self.team_list_local_path,
                        self.team_list_tablet_path,
                        validate_file,
                    ):
                        self.devices_with_list.add(device)
                        print(f"Loaded {self.team_list_local_path} to {device_name}")
                    else:
                        # Give both serial number and device name in warning
                        utils.log_warning(
                            f"FAILED sending {self.team_list_local_path} to {device_name} ({device})"
                        )
            # Update connected devices before checking if program should exit
            self.devices = set(adb_communicator.get_attached_devices())
            if (
                self.devices == self.devices_with_schedule
                and self.devices == self.devices_with_list
            ):
                # Print blank lines for visual distinction
                print("\n")
                # Schedule has been loaded onto all connected devices
                if self.send_match_schedule:
                    if len(self.devices_with_schedule) != 1:
                        print(
                            f"Match schedule loaded onto {len(self.devices_with_schedule)} devices."
                        )
                    else:
                        print("Match schedule loaded onto 1 device.")
                if len(self.devices_with_list) != 1:
                    print(f"Team list loaded onto {len(self.devices_with_list)} devices.")
                else:
                    print("Team list loaded onto 1 device.")
                    break


def argument_parser():
    parse = argparse.ArgumentParser()
    parse.add_argument("-g", action="store_true", help="Generate match_schedule and team_list only")
    parse.add_argument(
        "-s", action="store_true", help="Generate and Send match_schedule and team_list"
    )
    return parse.parse_args()


if __name__ == "__main__":
    # Set paths to read from and write to
    match_schedule_tablet_path = "/storage/self/primary/Download/match_schedule.json"
    match_schedule_local_path = utils.create_file_path("data/match_schedule.json")
    team_list_tablet_path = "/storage/self/primary/Download/team_list.json"
    team_list_local_path = utils.create_file_path("data/team_list.json")

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
