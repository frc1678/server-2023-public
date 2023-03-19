#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Houses several functions to generate random qr data"""
import random

from calculations import compression
import utils
from calculations.generate_random_value import generate_random_value

SCHEMA = utils.read_schema("schema/match_collection_qr_schema.yml")


def generate_timeline():
    """Generates example timeline data for a TIM"""
    final_timeline = []
    action_amount = random.randint(0, 30)
    if action_amount == 0:
        return final_timeline
    end_time = random.randint(0, 5)
    times = [int(end_time + ((x - 1) * (150 / action_amount))) for x in range(1, action_amount + 1)]
    # 10% chance for a team to go incap if it has enough actions left
    if random.randint(0, 9) == 9 and len(times) > 1:
        incap_time = random.randint(0, len(times) - 2)
        final_timeline.append({"action_type": "end_incap", "time": times.pop(incap_time)})
        final_timeline.append({"action_type": "start_incap", "time": times.pop(incap_time)})
        # If there are no actions left, just return the timeline
        if len(times) == 0:
            return final_timeline
    teleop_start = random.choice(times)
    # For all other times, fill in with normal scores
    for time in times:
        scores = [
            action
            for action in SCHEMA["action_type"]
            if "score_cone" in action or "score_cube" in action
        ]
        score_choice = random.choice(scores)
        if time < teleop_start:
            final_timeline.append({"action_type": score_choice, "time": time, "in_teleop": False})
        elif time == teleop_start:
            final_timeline.append({"action_type": "to_teleop", "time": time, "in_teleop": True})
        else:
            final_timeline.append({"action_type": score_choice, "time": time, "in_teleop": True})
    return final_timeline


def generate_generic_data(match_number=0, scout_name=None):
    """Generates example generic data for objective and subjective TIMs"""
    final_data = {}
    # Fills the dictionary with random data based on type
    for data_field, info in SCHEMA["generic_data"].items():
        # If the data_field starts with an underscore, it is a metacharacter
        if not data_field.startswith("_"):
            final_data[data_field] = generate_random_value(info[1], data_field)

    # schema_version should not be random
    final_data["schema_version"] = SCHEMA["schema_file"]["version"]

    # If data fields are passed in, make them not random
    if match_number != 0:
        final_data["match_number"] = match_number
    if scout_name is not None:
        final_data["scout_name"] = scout_name
    return final_data


def generate_obj_tim(team_number="0", scout_id=0, match_number=0, scout_name=None):
    """Generates example data for objective TIMs"""
    final_data = {}
    # Fills the dictionary with random data based on type
    for data_field, info in SCHEMA["objective_tim"].items():
        if not data_field.startswith("_") and data_field != "timeline":
            final_data[data_field] = generate_random_value(info[1], data_field)

    # If data fields are passed in, make them not random
    if team_number != "0":
        final_data["team_number"] = team_number
    if scout_id != 0:
        final_data["scout_id"] = scout_id

    # Generate generic data for the TIM
    final_data.update(generate_generic_data(match_number, scout_name))

    # Generate timeline data for the TIM
    final_data["timeline"] = generate_timeline()

    # Return final data compressed into a qr string
    return compression.compress_obj_tim(final_data)


def generate_subj_aim(team_list=None, match_number=0, scout_name=None):
    """Generates example data for subjective TIMs"""
    final_data = []
    # If the team_list isn't pre-populated, generate random teams
    if team_list is None:
        team_list = [generate_random_value("str", "team_number") for x in range(3)]
    generic_data = generate_generic_data(match_number, scout_name)
    for team in team_list:
        team_data = {}
        for data_field, info in SCHEMA["subjective_aim"].items():
            if not data_field.startswith("_"):
                # Generate an integer in range for specified datapoints, else generate any random integer
                if data_field == "quickness_score" or data_field == "field_awareness_score":
                    team_data[data_field] = random.randrange(1, 3)
                else:
                    team_data[data_field] = generate_random_value(info[1], data_field)
        team_data["team_number"] = team
        # Generate generic data for the TIM
        team_data.update(generic_data)
        final_data.append(team_data)

    # Return final data compressed into a qr string
    return compression.compress_subj_aim(final_data)
