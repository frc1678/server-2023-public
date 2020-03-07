#!/usr/bin/env python3
"""Calculate objective team data from Team in Match (TIM) data."""
# External imports
import yaml
# Internal imports
import local_database_communicator
import utils


def calculate_obj_team(team):
    """Calculate data for given team using objective calculated TIMs"""
    team_info = {}
    # list of TIMs that the team has been in:
    tims = local_database_communicator.read_dataset('processed.calc_obj_tim', team_number=team)
    # Calculate averages
    for calculation, schema in SCHEMA['averages'].items():
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
    # Calculate counts
    for calculation, schema in SCHEMA['counts'].items():
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


# Used for converting to a type that is given as a string
STR_TYPES = {
    'str': str,
    'float': float,
    'int': int
}

with open(utils.create_file_path('schema/calc_obj_team_schema.yml')) as file:
    SCHEMA = yaml.load(file, yaml.Loader)
