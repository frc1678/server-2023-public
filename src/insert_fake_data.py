#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Writes autogenerated fake data to database for viewer to test with
Remember to run server.py after running this file so that the raw data is calculated and pushed to cloud."""

from data_transfer import database
import generate_test_qrs
import generate_test_data
import qr_code_uploader
import utils
import random
import string
import os
from typing import List
from server import Server


def print_bold_red(text: str) -> None:
    print(f"\u001b[31m\u001b[1m{text}\u001b[0m")


# Begin by creating a fake list of teams and a fake dictionary of scouts
# That way the fake data will be realistic enough to actually be useful :)
def fake_name() -> str:
    """Returns a human sounding name"""
    num_letters = random.randint(4, 10)
    name = random.choice(string.ascii_uppercase)
    name += "".join([random.choice(string.ascii_lowercase) for letter in range(num_letters - 1)])
    # 25% chance of adding a last initial
    if random.randint(1, 4) == 1:
        initial = " " + random.choice(string.ascii_uppercase) + "."
        name += initial
    return name


def insert_fake_qr_data() -> List[str]:
    """Uses functions from generate_test_qrs to create fake qr codes."""
    qr_codes = []
    for match in MATCHES:
        match_num = match["match_number"]
        red = [team.split("frc")[1] for team in match["alliances"]["red"]["team_keys"]]
        blue = [team.split("frc")[1] for team in match["alliances"]["blue"]["team_keys"]]
        obj_scouts_in_match = list(obj_scouts.items())
        subj_scouts_in_match = random.sample(list(subj_scouts), 2)
        for alliance in [red, blue]:
            # Insert objective team in match qrs
            for team in alliance:
                # Make 1 qr for each of the 3 scouts per team
                for i in range(3):
                    scout = obj_scouts_in_match.pop()
                    scout_id = scout[0]
                    scout_name = scout[1]
                    qr_codes.append(
                        generate_test_qrs.generate_obj_tim(team, scout_id, match_num, scout_name)
                    )
            # Insert subjective alliance qrs
            subj_scout = subj_scouts_in_match[0]
            qr_codes.append(generate_test_qrs.generate_subj_aim(alliance, match_num, subj_scout))
    qr_code_uploader.upload_qr_codes(qr_codes)
    return qr_codes


def insert_fake_non_qr_data() -> List:
    """Use generate_test_data to generate fake data and insert into dictionary.
    Also returns the fake objective and subjective data, respectively"""
    fake_obj_pit_data_generator = generate_test_data.DataGenerator(
        "schema/obj_pit_collection_schema.yml", PATH_TO_MATCH_SCHEDULE
    )
    fake_subj_pit_data_generator = generate_test_data.DataGenerator(
        "schema/subj_pit_collection_schema.yml", PATH_TO_MATCH_SCHEDULE
    )

    # Change team numbers to match actual team numbers
    obj = fake_obj_pit_data_generator.get_data(len(TEAMS))
    for team_num, data_set in zip(TEAMS, obj):
        data_set.update({"team_number": team_num})

    try:
        local_database.insert_documents("raw_obj_pit", obj)
    except:
        error_msg = "Cannot insert fake raw data without overwriting existing data"
        print_bold_red(f"Error: {error_msg}")
    return obj


def insert_all_data() -> None:
    insert_fake_qr_data()
    insert_fake_non_qr_data()
    utils.log_info("Done inserting data. Please run server to calculate and upload to cloud")


local_database = database.Database(port=1678)
NUM_OBJ_SCOUTS = 18
NUM_SUBJ_SCOUTS = 3
PATH_TO_MATCH_SCHEDULE = utils.create_file_path(f"data/{utils.TBA_EVENT_KEY}_match_schedule.csv")
if not os.path.exists(PATH_TO_MATCH_SCHEDULE):
    # For testing purposes, let this work even when there is no match schedule
    print_bold_red(
        f"Watch out! {PATH_TO_MATCH_SCHEDULE} doesn't exist, so we'll just make a "
        "fake match schedule to work with instead"
    )
    PATH_TO_MATCH_SCHEDULE = None

# Ensure no duplicate scout names by using sets
obj_scout_names = set()
subj_scout_names = set()
while len(obj_scout_names) < NUM_OBJ_SCOUTS:
    obj_scout_names.add(fake_name())
while len(subj_scout_names) < NUM_SUBJ_SCOUTS:
    subj_scout_names.add(fake_name())
# Dictionary of scout ids to scout names
# Scout ID is one greater than the index, since it starts counting at 1
obj_scouts = {index + 1: name for index, name in zip(range(NUM_OBJ_SCOUTS), list(obj_scout_names))}
# Super scouts don't have IDs, just names
subj_scouts = list(subj_scout_names)


if __name__ == "__main__":

    from data_transfer import tba_communicator

    TEAMS = [
        team["team_number"]
        for team in tba_communicator.tba_request(f"event/{Server.TBA_EVENT_KEY}/teams/simple")
    ]
    MATCHES = [
        match
        for match in tba_communicator.tba_request(f"event/{Server.TBA_EVENT_KEY}/matches/simple")
        if match["comp_level"] == "qm"
    ]
    insert_all_data()
else:
    # Define constants for how many teams and matches we want
    NUM_TEAMS = 42
    NUM_MATCHES = 118
    # Create a fake list of teams
    TEAMS = {"1678"}
    while len(TEAMS) < NUM_TEAMS:
        TEAMS.add(str(random.randint(1, 9999)))
    TEAMS = list(TEAMS)
    MATCHES = []
    # This match schedule doesn't need to be realistic, only good enough for pytest to pass
    for match_number in range(1, NUM_MATCHES + 1):
        current_match = {"match_number": match_number}
        teams_in_current_match = random.sample(TEAMS, 6)
        red = [f"frc{team}" for team in teams_in_current_match[0:3]]
        blue = [f"frc{team}" for team in teams_in_current_match[3:6]]
        current_match["alliances"] = {
            "red": {"team_keys": red},
            "blue": {"team_keys": blue},
        }
        MATCHES.append(current_match)
