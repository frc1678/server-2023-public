#!/usr/bin/env python3
# Copyright (c) 2020 FRC Team 1678: Citrus Circuits
"""This file tests the functions provided in tba_team that
don't require the database.
"""

from calculations import tba_team
import pytest


def test_calculate_avg_climb_successful_time_empty():
    """Makes sure that two empty sets of data return 0, as claimed in the documentation"""
    assert tba_team.calculate_avg_climb_successful_time([], []) == 0


def test_calculate_avg_climb_successful_time_filled():
    """Testing an actual non-empty data set"""
    assert (
        tba_team.calculate_avg_climb_successful_time(
            [
                {
                    'climb_time': 4,
                    'match_number': 254,  # Not in tba_tims, so "4" shouldn't affect average
                },
                # The only two sets of data that should matter are the two below,
                # so the average should be 7.
                {'climb_time': 5, 'match_number': 1678},
                {'climb_time': 9, 'match_number': 5201},
            ],
            [
                {
                    'climb': True,
                    'match_number': 1678,
                },
                {
                    'climb': False,  # This set should be dropped if no climb, so the average should be 7
                    'match_number': 254,
                },
                {'climb': True, 'match_number': 5201},
            ],
        )
        == 7
    )


def test_tim_counts():
    print(tba_team.SCHEMA)
    assert (
        tba_team.tim_counts(
            [
                {
                    'auto_balls_high': 67,
                    'auto_balls_low': 31,
                    'climb_time': 8,
                    'confidence_rating': 86,
                    'control_panel_position': False,
                    'control_panel_rotation': True,
                    'incap': 8,
                    'match_number': 8,
                    'team_number': 254,
                    'tele_balls_high': 97,
                    'tele_balls_low': 11,
                }
            ],
            [
                {
                    'auto_line': True,
                    'climb': True,
                    'park': False,
                    'level_climb': True,
                    'match_number': 8,
                    'team_number': 254,
                }
            ],
        )['climb_all_successes']
        == 1
    )

    # Let's just make up some data. Here, climb is False, so there should be no climb successes.
    assert (
        tba_team.tim_counts(
            [
                {
                    'match_number': 11,
                    'team_number': 254,
                    'auto_balls_low': 5,
                    'auto_balls_high': 5,
                    'tele_balls_low': 21,
                    'tele_balls_high': 22,
                    'control_panel_rotation': True,
                    'control_panel_position': False,
                    'incap': 5,
                    'climb_time': 4,
                    'confidence_ranking': 3,
                    'match_number': 11,
                }
            ],
            [
                {
                    'auto_line': True,
                    'climb': False,
                    'park': False,
                    'level_climb': True,
                    'match_number': 11,
                    'team_number': 254,
                }
            ],
        )['climb_all_successes']
        == 0
    )
