#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Defines functions to consolidate and calculate Team In Match (TIM) data.

Usage: server.py calls update_calc_obj_tims to consolidate & calculate specified TIMs.
"""
# External imports
import statistics
import copy
# Internal imports
import local_database_communicator
import utils


# Functions for consolidating TIMs:
def modes(nums):
    """Returns the most frequently occurring items in the given list, nums"""
    if len(nums) == 0:
        return []
    # Create a dictionary of numbers to how many times they occur in the list
    frequencies = {}
    for num in nums:
        frequencies[num] = 1 + frequencies.get(num, 0)
    # How many times each mode occurs in nums:
    max_occurrences = max(frequencies.values())
    return [num for num, frequency in frequencies.items() if frequency == max_occurrences]


def consolidate_nums(nums):
    """Given numbers reported by multiple scouts, estimates actual number

    nums is a list of numbers, representing action counts or times, reported by each scout
    Currently tries to consolidate using only the reports from scouts on one robot,
    but future improvements might change the algorithm to account for other alliance members,
    since TBA can give us the total action counts for the alliance
    """
    mean = utils.avg(nums)
    if mean in nums or len(nums) == 0:
        # Avoid getting a divide by zero error when calculating standard deviation
        return round(mean)
    # If two or more scouts agree, automatically go with what they say
    if len(nums) > len(set(nums)):
        # Still need to consolidate, in case there are multiple modes
        return consolidate_nums(modes(nums))
    # Population standard deviation:
    std_dev = statistics.pstdev(nums)
    # Calculate weighted average, where the weight for each num is its reciprocal square z-score
    # That way, we account less for data farther from the mean
    z_scores = [(num - mean) / std_dev for num in nums]
    weights = [1 / z ** 2 for z in z_scores]
    float_nums = utils.avg(nums, weights)
    return round(float_nums)


def consolidate_bools(bools):
    """Given a list of booleans reported by multiple scouts, returns the actual value"""
    bools = modes(bools)
    if len(bools) == 1:
        # Go with the majority
        return bools[0]
    # Scouts are evenly split, so just go with False
    return False


# Functions for calculating consolidated TIMs:
def filter_timeline_actions(tim, **filters):
    """tim (dict) contains info for one TIM"""
    actions = tim['timeline']
    for field, required_value in filters.items():
        if field == 'time':
            # Times are given as closed intervals: either [0,134] or [135,150]
            acceptable_times = range(required_value[0], required_value[1] + 1)
            actions = filter(lambda action: action['time'] in acceptable_times, actions)
        else:
            # Removes actions for which action[field] != required_value
            actions = filter(lambda action: action[field] == required_value, actions)
        # filter returns an iterable object
        actions = list(actions)
    return actions


def count_timeline_actions(tim, **filters):
    """Returns the number of actions in one TIM timeline that meets the required filters"""
    return len(filter_timeline_actions(tim, **filters))


def total_time_between_actions(tim, start_action, end_action):
    """Returns total number of seconds spent between two types of actions for a given TIM

    start_action and end_action are the names (types) of those two actions,
    such as start_incap and end_climb.
    """
    start_actions = filter_timeline_actions(tim, action_type=start_action)
    end_actions = filter_timeline_actions(tim, action_type=end_action)
    total_time = 0
    # Match scout app should automatically add an end action at the end of the match,
    # if there isn't already an end action after the last start action. That way there are the
    # same number of start actions and end actions.
    for start, end in zip(start_actions, end_actions):
        total_time += start['time'] - end['time']
    return total_time


def calculate_tim(unconsolidated_tims):
    """Given a consolidated TIM, returns a calculated TIM

    tim (dict) contains TIM data.
    """
    # raises a ValueError if there are not TIMs in unconsolidated_tims
    if len(unconsolidated_tims) == 0:
        raise ValueError('Watch out! You are trying to consolidate a list of zero TIMs')
    calculated_tim = {}
    # Timeline counts
    for calculation, filters in SCHEMA['timeline_counts'].items():
        unconsolidated_counts = []
        for tim in unconsolidated_tims:
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop('type')
            new_count = count_timeline_actions(tim, **filters_)
            if not isinstance(new_count, TYPE_CHECK_DICT[expected_type]):
                raise TypeError(f'Expected {new_count} calculation to be a {expected_type}')
            unconsolidated_counts.append(new_count)
        calculated_tim[calculation] = consolidate_nums(unconsolidated_counts)
    # Timeline bools
    for calculation, filters in SCHEMA['timeline_bools'].items():
        unconsolidated_bools = []
        for tim in unconsolidated_tims:
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop('type')
            new_bool = bool(count_timeline_actions(tim, **filters_))
            if not isinstance(new_bool, TYPE_CHECK_DICT[expected_type]):
                raise TypeError(f'Expected {new_bool} calculation to be a {expected_type}')
            unconsolidated_bools.append(new_bool)
        calculated_tim[calculation] = consolidate_bools(unconsolidated_bools)
    # Cycle times
    for calculation, action_types in SCHEMA['timeline_cycle_time'].items():
        unconsolidated_cycle_times = []
        for tim in unconsolidated_tims:
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(action_types)
            expected_type = filters_.pop('type')
            # action_types is a list of dictionaries, where each dictionary is
            # "action_type" to the name of either the start or end action
            new_cycle_time = total_time_between_actions(
                tim, action_types['start_action'], action_types['end_action'])
            if not isinstance(new_cycle_time, TYPE_CHECK_DICT[expected_type]):
                raise TypeError(f'Expected {new_cycle_time} calculation to be a {expected_type}')
            unconsolidated_cycle_times.append(new_cycle_time)
        calculated_tim[calculation] = consolidate_nums(unconsolidated_cycle_times)
    # Use any of the unconsolidated TIMs to get the team and match number,
    # since that should be the same for each unconsolidated TIM
    calculated_tim['match_number'] = unconsolidated_tims[0]['match_number']
    calculated_tim['team_number'] = unconsolidated_tims[0]['team_number']
    # confidence_rating is the number of scouts that scouted one robot
    calculated_tim['confidence_ranking'] = len(unconsolidated_tims)
    return calculated_tim


def update_calc_obj_tims(tims):
    """tims (list): TIMs to be calculated.

    Each TIM within the list tims is a dictionary with keys 'team_number' and 'match_number'.
    Those dictionaries might be missing keys (for example, if match_number is given but team_number
    isn't, we should calculate all TIMs for the match).
    """
    tims_without_missing_keys = []
    for tim in tims:
        unconsolidated_tims = (local_database_communicator.read_dataset(
            'processed.unconsolidated_obj_tim', **tim))
        for unconsolidated_tim in unconsolidated_tims:
            new_tim = {'team_number': unconsolidated_tim['team_number'],
                       'match_number': unconsolidated_tim['match_number']}
            if new_tim not in tims_without_missing_keys:
                tims_without_missing_keys.append(new_tim)
    # Now actually calculate TIMs
    calculated_tims = []
    for tim in tims_without_missing_keys:
        # Because that code above, we can be sure that each tim will clearly refer to one team in
        # one match, since it won't be missing the key 'team_number' or the key 'match_number'
        unconsolidated_tims = (local_database_communicator.read_dataset(
            'processed.unconsolidated_obj_tim', **tim))
        calculated_tim = utils.catch_function_errors(calculate_tim, unconsolidated_tims)
        calculated_tims.append(calculated_tim)
    return calculated_tims


TYPES_CONVERSION_DICT = {
    'float': float,
    'int': int,
    'str': str,
    'bool': utils.get_bool
}

TYPE_CHECK_DICT = {
    'float': float,
    'int': int,
    'str': str,
    'bool': bool
}

SCHEMA = utils.read_schema('schema/calc_obj_tim_schema.yml')
