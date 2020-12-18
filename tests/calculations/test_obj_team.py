#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
import pytest
from src.calculations import obj_team


def test_averaging_low_and_high_goals_together():
    """Tests calculate_averages function from src/calculations/obj_team.py

    In this case, tests only the calculations auto_avg_balls_total and tele_avg_balls_total
    """
    tims = [
        {'auto_balls_low': 1, 'auto_balls_high': 2, 'tele_balls_low': 3, 'tele_balls_high': 4},
        {
            'auto_balls_low': 5,
            'auto_balls_high': 6,
            'tele_balls_low': 7,
            'tele_balls_high': 8,
            'the coolest': 'Eugene Chen',
        },
    ]
    schema_for_averages = {
        'auto_avg_balls_total': {
            'tim_fields': ['auto_balls_low', 'auto_balls_high'],
            'type': 'float',
        },
        'tele_avg_balls_total': {
            'tim_fields': ['tele_balls_low', 'tele_balls_high'],
            'type': 'float',
        },
    }
    expected_output = {'auto_avg_balls_total': 7.0, 'tele_avg_balls_total': 11.0}
    assert obj_team.calculate_averages(tims, schema_for_averages) == expected_output


def test_calculating_avg_incap_time():
    # The data field 'incap' in TIMs is the average number of seconds the robot spent incapacitated
    tims = [{'incap': 0.0}, {'incap': 0.0}, {'incap': 118}, {'incap': 0}]
    schema_for_averages = {'avg_incap_time': {'tim_fields': ['incap'], 'type': 'float'}}
    expected_output = {'avg_incap_time': 29.5}
    assert obj_team.calculate_averages(tims, schema_for_averages) == expected_output


def test_misspelled_data_field():
    tims = [{'incap': 0.0}, {'incap': 0.0}, {'incap': 118}, {'incap': 0}]
    schema_for_averages = {'avg_incap_time': {'tim_fields': ['incapacitated'], 'type': 'float'}}
    # Since the data field was called 'incapacitated' in the schema and 'incap' in the actual TIMs,
    # this should throw a KeyError
    expected_output = {'avg_incap_time': 29.5}
    with pytest.raises(KeyError):
        assert obj_team.calculate_averages(tims, schema_for_averages) == expected_output


def test_counts():
    """Just a normal test case for the function obj_team.calculate_counts as it is supposed to be used"""
    tims = [
        {'control_panel_rotation': True, 'control_panel_position': True, 'climb_time': 0},
        {'control_panel_rotation': True, 'control_panel_position': False, 'climb_time': 20},
        {'control_panel_rotation': False, 'control_panel_position': False, 'climb_time': 5},
    ]
    schema_for_counts = {
        'tele_cp_rotation_successes': {
            'tim_fields': {'control_panel_rotation': True},
            'type': 'int',
        },
        'tele_cp_position_successes': {
            'tim_fields': {'control_panel_position': True},
            'type': 'int',
        },
        'climb_all_attempts': {'tim_fields': {'not': {'climb_time': 0}}, 'type': 'int'},
    }
    expected_output = {
        'tele_cp_rotation_successes': 2,
        'tele_cp_position_successes': 1,
        'climb_all_attempts': 2,
    }
    assert obj_team.calculate_counts(tims, schema_for_counts) == expected_output


def test_wonky_schema_for_counts():
    """Since the schema for this is weird, make sure it fails if the schema is extra wonky"""
    tims = [
        {'control_panel_rotation': True, 'control_panel_position': True, 'climb_time': 0},
        {'control_panel_rotation': True, 'control_panel_position': False, 'climb_time': 20},
        {'control_panel_rotation': False, 'control_panel_position': False, 'climb_time': 5},
    ]
    schema_for_counts = {
        'climb_all_attempts': {'tim_fields': {'climb_success': True}, 'type': 'int'}
    }
    expected_output = {'climb_all_attempts': 2}
    with pytest.raises(KeyError):
        assert obj_team.calculate_counts(tims, schema_for_counts) == expected_output
