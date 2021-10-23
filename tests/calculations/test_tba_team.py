#!/usr/bin/env python3
# Copyright (c) 2020 FRC Team 1678: Citrus Circuits
"""This file tests the functions provided in tba_team that
don't require the database.
"""

from calculations import tba_team
from data_transfer import database
import utils
from server import Server

import pytest


@pytest.mark.clouddb
class TestTBATeamCalc:
    def setup_method(self, method):
        self.test_server = Server()
        self.test_calc = tba_team.TBATeamCalc(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ['obj_tim', 'obj_team', 'tba_tim']
        assert self.test_calc.server == self.test_server

    def test_calculate_avg_climb_successful_time_empty(self):
        """Makes sure that two empty sets of data return 0, as claimed in the documentation"""
        assert self.test_calc.calculate_avg_climb_successful_time([], []) == 0

    def test_calculate_avg_climb_successful_time_filled(self):
        """Testing an actual non-empty data set"""
        assert (
            self.test_calc.calculate_avg_climb_successful_time(
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

    def test_tim_counts(self):
        assert (
            self.test_calc.tim_counts(
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
            self.test_calc.tim_counts(
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

    def test_run(self):
        teams = {
            "api_url": f'event/{Server.TBA_EVENT_KEY}/teams/simple',
            "data": [
                {
                    'city': 'Atascadero',
                    'country': 'USA',
                    'key': 'frc973',
                    'nickname': 'Greybots',
                    'state_prov': 'California',
                    'team_number': 973,
                },
                {
                    'city': 'Davis',
                    'country': 'USA',
                    'key': 'frc1678',
                    'nickname': 'Citrus Circuits',
                    'state_prov': 'California',
                    'team_number': 1678,
                },
            ],
        }
        obj_teams = [
            {
                'auto_avg_balls_low': 54.0875,
                'auto_avg_balls_high': 93.446,
                'auto_avg_balls_total': 60.9901,
                'tele_avg_balls_low': 39.9281,
                'tele_avg_balls_high': 32.3048,
                'tele_avg_balls_total': 26.672,
                'avg_incap_time': 48.0607,
                'tele_cp_rotation_successes': 8,
                'tele_cp_position_successes': 13,
                'climb_all_attempts': 52,
                'team_number': 973,
            },
            {
                'auto_avg_balls_low': 64.6622,
                'auto_avg_balls_high': 0.1922,
                'auto_avg_balls_total': 81.2747,
                'tele_avg_balls_low': 83.7899,
                'tele_avg_balls_high': 73.0669,
                'tele_avg_balls_total': 23.611,
                'avg_incap_time': 49.0128,
                'tele_cp_rotation_successes': 8,
                'tele_cp_position_successes': 75,
                'climb_all_attempts': 59,
                'team_number': 1678,
            },
        ]
        obj_tims = [
            {
                'auto_balls_low': 66,
                'auto_balls_high': 61,
                'tele_balls_low': 18,
                'tele_balls_high': 45,
                'control_panel_rotation': True,
                'control_panel_position': False,
                'incap': 14,
                'climb_time': 21,
                'confidence_rating': 30,
                'team_number': 973,
                'match_number': 1,
            },
            {
                'auto_balls_low': 30,
                'auto_balls_high': 59,
                'tele_balls_low': 57,
                'tele_balls_high': 1,
                'control_panel_rotation': True,
                'control_panel_position': True,
                'incap': 22,
                'climb_time': 3,
                'confidence_rating': 68,
                'team_number': 973,
                'match_number': 2,
            },
            {
                'auto_balls_low': 84,
                'auto_balls_high': 92,
                'tele_balls_low': 40,
                'tele_balls_high': 67,
                'control_panel_rotation': False,
                'control_panel_position': False,
                'incap': 18,
                'climb_time': 64,
                'confidence_rating': 2,
                'team_number': 973,
                'match_number': 3,
            },
            {
                'auto_balls_low': 47,
                'auto_balls_high': 76,
                'tele_balls_low': 34,
                'tele_balls_high': 81,
                'control_panel_rotation': True,
                'control_panel_position': True,
                'incap': 17,
                'climb_time': 46,
                'confidence_rating': 31,
                'team_number': 1678,
                'match_number': 1,
            },
            {
                'auto_balls_low': 25,
                'auto_balls_high': 54,
                'tele_balls_low': 81,
                'tele_balls_high': 59,
                'control_panel_rotation': True,
                'control_panel_position': True,
                'incap': 93,
                'climb_time': 35,
                'confidence_rating': 14,
                'team_number': 1678,
                'match_number': 2,
            },
            {
                'auto_balls_low': 54,
                'auto_balls_high': 49,
                'tele_balls_low': 88,
                'tele_balls_high': 74,
                'control_panel_rotation': True,
                'control_panel_position': True,
                'incap': 15,
                'climb_time': 97,
                'confidence_rating': 77,
                'team_number': 1678,
                'match_number': 3,
            },
        ]
        tba_tims = [
            {
                'auto_line': False,
                'climb': True,
                'park': False,
                'level_climb': True,
                'match_number': 1,
                'team_number': 973,
            },
            {
                'auto_line': False,
                'climb': True,
                'park': False,
                'level_climb': False,
                'match_number': 2,
                'team_number': 973,
            },
            {
                'auto_line': True,
                'climb': True,
                'park': True,
                'level_climb': False,
                'match_number': 3,
                'team_number': 973,
            },
            {
                'auto_line': True,
                'climb': False,
                'park': True,
                'level_climb': False,
                'match_number': 1,
                'team_number': 1678,
            },
            {
                'auto_line': False,
                'climb': True,
                'park': False,
                'level_climb': False,
                'match_number': 2,
                'team_number': 1678,
            },
            {
                'auto_line': True,
                'climb': False,
                'park': True,
                'level_climb': True,
                'match_number': 3,
                'team_number': 1678,
            },
        ]
        expected_results = [
            {
                "team_number": 973,
                "auto_avg_balls_inner": 0,
                "auto_avg_balls_outer": 93.446,
                "auto_high_balls_percent_inner": 0,
                "auto_line_successes": 1,
                "climb_all_success_avg_time": 29.333333333333332,
                "climb_all_successes": 3,
                "climb_level_successes": 1,
                "climb_percent_success": 0.057692307692307696,
                "park_successes": 1,
                "team_name": "Greybots",
                "tele_avg_balls_inner": 0,
                "tele_avg_balls_outer": 32.3048,
                "tele_high_balls_percent_inner": 0,
            },
            {
                "team_number": 1678,
                "auto_high_balls_percent_inner": 0,
                "auto_avg_balls_inner": 0,
                "auto_avg_balls_outer": 0.1922,
                "auto_line_successes": 2,
                "climb_all_success_avg_time": 35,
                "climb_all_successes": 1,
                "climb_level_successes": 1,
                "climb_percent_success": 0.01694915254237288,
                "park_successes": 2,
                "team_name": "Citrus Circuits",
                "tele_high_balls_percent_inner": 0,
                "tele_avg_balls_inner": 0,
                "tele_avg_balls_outer": 73.0669
            },
        ]
        self.test_server.db.insert_documents('tba_cache', teams)
        self.test_server.db.insert_documents('obj_tim', obj_tims)
        self.test_server.db.insert_documents('obj_team', obj_teams)
        self.test_server.db.insert_documents('tba_tim', tba_tims)
        self.test_calc.run()
        result = self.test_server.db.find('tba_team')
        assert len(result) == 2
        for document in result:
            del document['_id']
            assert document in expected_results
