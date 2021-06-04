#!/usr/bin/env python3
"""Calculate objective team data from Team in Match (TIM) data."""

import utils
from typing import List, Dict
from calculations import base_calculations
from statistics import pstdev


class OBJTeamCalc(base_calculations.BaseCalculations):
    """Runs OBJ Team calculations"""

    # Get the last section of each entry (so foo.bar.baz becomes baz)
    SCHEMA = utils.unprefix_schema_dict(utils.read_schema('schema/calc_obj_team_schema.yml'))

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ['obj_tim']

    def get_action_counts(self, tims: List[Dict]):
        """Gets a list of times each team completed a certain action by tim for averages
        and standard deviations.
        """
        tim_action_counts = {}
        # Gathers all necessary schema fields
        tim_fields = set()
        for schema in {**self.SCHEMA['averages'], **self.SCHEMA['standard_deviations']}.values():
            tim_fields.add(schema['tim_fields'][0])
        for tim_field in tim_fields:
            # Gets the total number of actions across all tims
            tim_action_counts[tim_field] = [tim[tim_field.split('.')[1]] for tim in tims]
        return tim_action_counts

    def calculate_averages(self, tim_action_counts):
        """Creates a dictionary of calculated averages, called team_info,
        where the keys are the names of the calculations, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA['averages'].items():
            # Average the values for the tim_fields
            average = 0
            for tim_field in schema['tim_fields']:
                average += self.avg(tim_action_counts[tim_field])
            team_info[calculation] = average
        return team_info

    def calculate_standard_deviations(self, tim_action_counts):
        """Creates a dictionary of calculated standard deviations, called team_info,
        where the keys are the names of the calculation, and the values are the results
        """
        team_info = {}
        for calculation, schema in self.SCHEMA['standard_deviations'].items():
            # Take the standard deviation for the tim_field
            tim_field = schema['tim_fields'][0]
            standard_deviation = pstdev(tim_action_counts[tim_field])
            team_info[calculation] = standard_deviation
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
            team_info[calculation] = len(tims_that_meet_filter)
        return team_info

    def update_team_calcs(self, teams: list) -> list:
        """Calculate data for given team using objective calculated TIMs"""

        obj_team_updates = {}
        for team in teams:
            # Load team data from database
            obj_tims = self.server.db.find('obj_tim', team_number=team)
            tim_action_counts = self.get_action_counts(obj_tims)
            team_data = self.calculate_averages(tim_action_counts)
            team_data['team_number'] = team
            team_data.update(self.calculate_counts(obj_tims))
            team_data.update(self.calculate_standard_deviations(tim_action_counts))
            obj_team_updates[team] = team_data
        return list(obj_team_updates.values())

    def run(self):
        """Executes the OBJ Team calculations"""
        # Get oplog entries
        entries = self.entries_since_last()
        for update in self.update_team_calcs(self.find_team_list()):
            self.server.db.update_document(
                'obj_team', update, {'team_number': update['team_number']}
            )
