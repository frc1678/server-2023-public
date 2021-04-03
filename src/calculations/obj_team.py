#!/usr/bin/env python3
"""Calculate objective team data from Team in Match (TIM) data."""

import utils
from typing import List, Dict
from src.calculations import base_calculations


class OBJTeamCalc(base_calculations.BaseCalculations):
    """Runs OBJ Team calculations"""

    # Get the last section of each entry (so foo.bar.baz becomes baz)
    SCHEMA = utils.unprefix_schema_dict(utils.read_schema('schema/calc_obj_team_schema.yml'))
    STR_TYPES = {'str': str, 'float': float, 'int': int}

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ['obj_tim']
        # Used for converting to a type that is given as a string

    def calculate_averages(self, tims: List[Dict]):
        """Creates a dictionary of calculated averages, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA['averages'].items():
            # Find tims that meet required data field:
            tim_action_counts = []
            for tim in tims:
                # Gets the total number of actions for a single tim
                tim_action_counts.append(
                    sum([tim[tim_field.split(".")[1]] for tim_field in schema['tim_fields']])
                )
            if schema['type'] not in ['int', 'float']:
                raise TypeError(f'{calculation} should be a number in calc obj team schema')
            average = self.avg(tim_action_counts)
            team_info[calculation] = self.STR_TYPES[schema['type']](average)
        return team_info

    def filter_tims_for_counts(self, tims: List[Dict], schema):
        """Filters tims based on schema for count calculations"""
        tims_that_meet_filter = tims
        for key, value in schema['tim_fields'].items():
            if key != 'not':
                # Checks that the TIMs in their given field meet the filter
                tims_that_meet_filter = list(
                    filter(lambda tim: tim[key] == value, tims_that_meet_filter)
                )
            else:
                # not_field expects the output to be anything but the given filter
                # not_value is the filter that not_field shouldn't have
                for not_field, not_value in value.items():
                    # Checks that the TIMs in the 'not' field are anything other than the filter
                    tims_that_meet_filter = list(
                        filter(
                            lambda tim: tim.get(not_field, not_value) != not_value,
                            tims_that_meet_filter,
                        )
                    )
        return tims_that_meet_filter

    def calculate_counts(self, tims: List[Dict]):
        """Creates a dictionary of calculated counts, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA['counts'].items():
            tims_that_meet_filter = self.filter_tims_for_counts(tims, schema)
            team_info[calculation] = self.STR_TYPES[schema['type']](len(tims_that_meet_filter))
        return team_info

    def update_team_calcs(self, teams: list) -> list:
        """Calculate data for given team using objective calculated TIMs"""

        obj_team_updates = {}
        for team in teams:
            # Load team data from database
            obj_tims = self.server.db.find('obj_tim', team_number=team)
            team_data = self.calculate_averages(obj_tims)
            team_data['team_number'] = team
            team_data.update(self.calculate_counts(obj_tims))
            obj_team_updates[team] = team_data
        return list(obj_team_updates.values())

    def run(self):
        """Executes the OBJ Team calculations"""
        # Get oplog entries
        entries = self.entries_since_last()
        teams = set()
        # Check if changes need to be made to teams
        if self.entries_since_last() is not None:
            for entry in entries:
                # Prevents error from not having a team num
                if 'team_number' in entry['o'].keys():
                    teams.add(entry['o']['team_number'])
        for update in self.update_team_calcs(list(teams)):
            self.server.db.update_document(
                'obj_team', update, {'team_number': update['team_number']}
            )
