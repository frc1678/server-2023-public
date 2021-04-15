#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Defines class methods to consolidate and calculate Team In Match (TIM) data."""

import copy
import statistics
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict


class ObjTIMCalcs(BaseCalculations):
    schema = utils.read_schema('schema/calc_obj_tim_schema.yml')
    type_check_dict = {'float': float, 'int': int, 'str': str, 'bool': bool}

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ['unconsolidated_obj_tim']

    def consolidate_nums(self, nums: List[Union[int, float]]) -> int:
        """Given numbers reported by multiple scouts, estimates actual number
        nums is a list of numbers, representing action counts or times, reported by each scout
        Currently tries to consolidate using only the reports from scouts on one robot,
        but future improvements might change the algorithm to account for other alliance members,
        since TBA can give us the total action counts for the alliance
        """
        mean = self.avg(nums)
        if len(nums) == 0 or mean in nums:
            # Avoid getting a divide by zero error when calculating standard deviation
            return round(mean)
        # If two or more scouts agree, automatically go with what they say
        if len(nums) > len(set(nums)):
            # Still need to consolidate, in case there are multiple modes
            return self.consolidate_nums(self.modes(nums))
        # Population standard deviation:
        std_dev = statistics.pstdev(nums)
        # Calculate weighted average, where the weight for each num is its reciprocal square z-score
        # That way, we account less for data farther from the mean
        z_scores = [(num - mean) / std_dev for num in nums]
        weights = [1 / z ** 2 for z in z_scores]
        float_nums = self.avg(nums, weights)
        return round(float_nums)

    def consolidate_bools(self, bools: list) -> bool:
        """Given a list of booleans reported by multiple scouts, returns the actual value"""
        bools = self.modes(bools)
        if len(bools) == 1:
            # Go with the majority
            return bools[0]
        # Scouts are evenly split, so just go with False
        return False

    def filter_timeline_actions(self, tim: dict, **filters) -> list:
        """Removes timeline actions that don't meet the filters and returns all the actions that do"""
        actions = tim['timeline']
        for field, required_value in filters.items():
            if field == 'time':
                # Times are given as closed intervals: either [0,134] or [135,150]
                actions = filter(
                    lambda action: required_value[0] <= action['time'] <= required_value[1], actions
                )
            else:
                # Removes actions for which action[field] != required_value
                actions = filter(lambda action: action[field] == required_value, actions)
            # filter returns an iterable object
            actions = list(actions)
        return actions

    def count_timeline_actions(self, tim: dict, **filters) -> int:
        """Returns the number of actions in one TIM timeline that meets the required filters"""
        return len(self.filter_timeline_actions(tim, **filters))

    def total_time_between_actions(self, tim: dict, start_action: str, end_action: str) -> int:
        """Returns total number of seconds spent between two types of actions for a given TIM

        start_action and end_action are the names (types) of those two actions,
        such as start_incap and end_climb.
        """
        start_actions = self.filter_timeline_actions(tim, action_type=start_action)
        end_actions = self.filter_timeline_actions(tim, action_type=end_action)
        total_time = 0
        # Match scout app should automatically add an end action at the end of the match,
        # if there isn't already an end action after the last start action. That way there are the
        # same number of start actions and end actions.
        return sum([start['time'] - end['time'] for start, end in zip(start_actions, end_actions)])

    def calculate_tim_counts(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated count based data fields"""
        calculated_tim = {}
        for calculation, filters in self.schema['timeline_counts'].items():
            unconsolidated_counts = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop('type')
            for tim in unconsolidated_tims:
                new_count = self.count_timeline_actions(tim, **filters_)
                if not isinstance(new_count, self.type_check_dict[expected_type]):
                    raise TypeError(f'Expected {new_count} calculation to be a {expected_type}')
                unconsolidated_counts.append(new_count)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_counts)
        return calculated_tim

    def calculate_tim_bools(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated bool data fields"""
        calculated_tim = {}
        for calculation, filters in self.schema['timeline_bools'].items():
            unconsolidated_bools = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop('type')
            for tim in unconsolidated_tims:
                new_bool = bool(self.count_timeline_actions(tim, **filters_))
                unconsolidated_bools.append(new_bool)
            calculated_tim[calculation] = self.consolidate_bools(unconsolidated_bools)
        return calculated_tim

    def calculate_tim_times(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated time data fields"""
        calculated_tim = {}
        for calculation, action_types in self.schema['timeline_cycle_time'].items():
            unconsolidated_cycle_times = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(action_types)
            expected_type = filters_.pop('type')
            for tim in unconsolidated_tims:
                # action_types is a list of dictionaries, where each dictionary is
                # "action_type" to the name of either the start or end action
                new_cycle_time = self.total_time_between_actions(
                    tim, action_types['start_action'], action_types['end_action']
                )
                if not isinstance(new_cycle_time, self.type_check_dict[expected_type]):
                    raise TypeError(
                        f'Expected {new_cycle_time} calculation to be a {expected_type}'
                    )
                unconsolidated_cycle_times.append(new_cycle_time)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_cycle_times)
        return calculated_tim

    def calculate_tim(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns a calculated TIM"""
        if len(unconsolidated_tims) == 0:
            raise ValueError('Cannot consolidate a list of zero TIMs')
        calculated_tim = {}
        calculated_tim.update(self.calculate_tim_counts(unconsolidated_tims))
        calculated_tim.update(self.calculate_tim_bools(unconsolidated_tims))
        calculated_tim.update(self.calculate_tim_times(unconsolidated_tims))
        # Use any of the unconsolidated TIMs to get the team and match number,
        # since that should be the same for each unconsolidated TIM
        calculated_tim['match_number'] = unconsolidated_tims[0]['match_number']
        calculated_tim['team_number'] = unconsolidated_tims[0]['team_number']
        # confidence_rating is the number of scouts that scouted one robot
        calculated_tim['confidence_ranking'] = len(unconsolidated_tims)
        return calculated_tim

    def update_obj_tim_calcs(self, tims: List[Dict[str, int]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': 1678, 'match_number': 69}"""
        calculated_tims = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find('unconsolidated_obj_tim', **tim)
            calculated_tims.append(self.calculate_tim(unconsolidated_obj_tims))
        return calculated_tims

    def run(self):
        """Executes the OBJ TIM calculations"""
        # Get oplog entries
        tims = []
        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) is not None:
            for entry in entries:
                tims.append(
                    {
                        'team_number': entry['o']['team_number'],
                        'match_number': entry['o']['match_number'],
                    }
                )
        unique_tims = []
        for tim in tims:
            if tim not in unique_tims:
                unique_tims.append(tim)

        for update in self.update_obj_tim_calcs(unique_tims):
            self.server.db.update_document(
                'obj_tim',
                update,
                {'team_number': update['team_number'], 'match_number': update['match_number']},
            )
