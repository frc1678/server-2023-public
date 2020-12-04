#!/usr/bin/env python3
"""Calculate objective team data from Team in Match (TIM) data."""

import os
import sys
import yaml


current_directory = os.path.dirname(os.path.realpath(__file__))
parent_directory = os.path.dirname(current_directory)
sys.path.append(parent_directory)
from data_transfer import local_database_communicator as ldc

import utils
from typing import List, Dict

def calculate_averages(tims: List[Dict], schema_for_averages: Dict):
    """ Creates a dictionary of calculated averages, called team_info,
    where the keys are the names of the calculations, and the values are the results """
    team_info = {}
    for calculation, schema in schema_for_averages.items():
        # Find tims that meet required data field:
        tim_action_counts = []
        for tim in tims:
            # Gets the total number of actions for a single tim
            tim_action_counts.append(sum(
                [tim[tim_field] for tim_field in schema['tim_fields']]))
        if schema['type'] in ['int', 'float']:
            average = utils.avg(tim_action_counts)
            average = STR_TYPES[schema['type']](average)
        else:
            raise TypeError(f'{calculation} should be a number in calc obj team schema')
        team_info[calculation] = average
    return team_info

def calculate_counts(tims, schema_for_counts):
    """ Creates a dictionary of calculated counts, called team_info,
    where the keys are the names of the calculations, and the values are the results """
    team_info = {}
    for calculation, schema in schema_for_counts.items():
        tims_that_meet_filter = tims
        for key, value in schema['tim_fields'].items():
            if key == 'not':
                # not_field expects the output to be anything but the given filter
                # not_value is the filter that not_field shouldn't have
                for not_field, not_value in value.items():
                    # Checks that the TIMs in the 'not' field are anything other than the filter
                    tims_that_meet_filter = list(filter(lambda tim: tim.get(
                        not_field, not_value) != not_value, tims_that_meet_filter))
            else:
                # Checks that the TIMs in their given field meet the filter
                tims_that_meet_filter = list(filter(
                    lambda tim: tim[key] == value, tims_that_meet_filter))
        team_info[calculation] = STR_TYPES[schema['type']](len(tims_that_meet_filter))
    return team_info


def calculate_obj_team(team):
    """Calculate data for given team using objective calculated TIMs"""
    # list of TIMs that the team has been in:
    tims = ldc.read_dataset('processed.calc_obj_tim', team_number=team)
    team_info = calculate_averages(tims, SCHEMA['averages'])
    team_info.update(calculate_counts(tims, SCHEMA['counts']))
    return team_info


# Used for converting to a type that is given as a string
STR_TYPES = {
    'str': str,
    'float': float,
    'int': int
}

with open(utils.create_file_path('schema/calc_obj_team_schema.yml')) as file:
    SCHEMA = yaml.load(file, yaml.Loader)
