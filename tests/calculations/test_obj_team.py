#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
import pytest
from calculations import obj_team
from server import Server


@pytest.mark.clouddb
class TestOBJTeamCalc:
    def setup_method(self, method):
        self.test_server = Server()
        self.test_calc = obj_team.OBJTeamCalc(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ['obj_tim']
        assert self.test_calc.server == self.test_server

    def test_averages(self):
        """Tests calculate_averages function from src/calculations/obj_team.py"""
        tims = [
            {
                'auto_balls_low': 1,
                'auto_balls_high': 2,
                'tele_balls_low': 3,
                'tele_balls_high': 4,
                'incap': 0.0,
            },
            {
                'auto_balls_low': 5,
                'auto_balls_high': 6,
                'tele_balls_low': 7,
                'tele_balls_high': 8,
                'incap': 15.0,
                'the coolest': 'Eugene Chen',
            },
        ]

        expected_output = {
            'auto_avg_balls_total': 7.0,
            'tele_avg_balls_total': 11.0,
            'auto_avg_balls_low': 3.0,
            'auto_avg_balls_high': 4.0,
            'tele_avg_balls_low': 5.0,
            'tele_avg_balls_high': 6.0,
            'avg_incap_time': 7.5,
        }
        action_counts = self.test_calc.get_action_counts(tims)
        assert self.test_calc.calculate_averages(action_counts) == expected_output

    def test_standard_deviations(self):
        """Tests calculate_standard_deviations function from src/calculations/obj_team.py"""
        tims = [
            {
                'auto_balls_low': 1,
                'auto_balls_high': 2,
                'tele_balls_low': 3,
                'tele_balls_high': 4,
                'incap': 0,
            },
            {
                'auto_balls_low': 5,
                'auto_balls_high': 6,
                'tele_balls_low': 7,
                'tele_balls_high': 8,
                'incap': 0,
            },
            {
                'auto_balls_low': 9,
                'auto_balls_high': 10,
                'tele_balls_low': 11,
                'tele_balls_high': 12,
                'incap': 0,
            },
        ]

        expected_output = {
            'auto_sd_balls_low': 3.265986323710904,
            'auto_sd_balls_high': 3.265986323710904,
            'tele_sd_balls_low': 3.265986323710904,
            'tele_sd_balls_high': 3.265986323710904,
        }
        action_counts = self.test_calc.get_action_counts(tims)
        assert self.test_calc.calculate_standard_deviations(action_counts) == expected_output

    def test_counts(self):
        """Tests calculate_counts function from src/calculations/obj_team.py"""
        tims = [
            {'control_panel_rotation': True, 'control_panel_position': True, 'climb_time': 0, 'match_number': 1},
            {'control_panel_rotation': True, 'control_panel_position': False, 'climb_time': 20, 'match_number': 2},
            {'control_panel_rotation': False, 'control_panel_position': False, 'climb_time': 5, 'match_number': 3},
        ]

        expected_output = {
            'tele_cp_rotation_successes': 2,
            'tele_cp_position_successes': 1,
            'climb_all_attempts': 2,
            'matches_played': 3
        }
        assert self.test_calc.calculate_counts(tims) == expected_output

    def test_run(self):
        """Tests run function from src/calculations/obj_team.py"""
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
                'auto_balls_high': 60,
                'tele_balls_low': 56,
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
                'tele_balls_high': 68,
                'control_panel_rotation': False,
                'control_panel_position': False,
                'incap': 18,
                'climb_time': 0,
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
                'auto_balls_high': 50,
                'tele_balls_low': 89,
                'tele_balls_high': 73,
                'control_panel_rotation': True,
                'control_panel_position': True,
                'incap': 16,
                'climb_time': 97,
                'confidence_rating': 77,
                'team_number': 1678,
                'match_number': 3,
            },
        ]
        expected_results = [
            {
                'team_number': 973,
                'auto_avg_balls_total': 131.0,
                'tele_avg_balls_total': 76.0,
                'auto_avg_balls_low': 60.0,
                'auto_avg_balls_high': 71.0,
                'tele_avg_balls_low': 38.0,
                'tele_avg_balls_high': 38.0,
                'auto_sd_balls_low': 22.44994432064365,
                'auto_sd_balls_high': 14.854853303438128,
                'tele_sd_balls_low': 15.57776192739723,
                'tele_sd_balls_high': 27.796882319185844,
                'avg_incap_time': 18.0,
                'tele_cp_rotation_successes': 2,
                'tele_cp_position_successes': 1,
                'climb_all_attempts': 2,
                'matches_played': 3
            },
            {
                "team_number": 1678,
                'auto_avg_balls_total': 102.0,
                'tele_avg_balls_total': 139.0,
                'auto_avg_balls_low': 42.0,
                'auto_avg_balls_high': 60.0,
                'tele_avg_balls_low': 68.0,
                'tele_avg_balls_high': 71.0,
                'auto_sd_balls_low': 12.355835328567093,
                'auto_sd_balls_high': 11.430952132988164,
                'tele_sd_balls_low': 24.26245384677046,
                'tele_sd_balls_high': 9.092121131323903,
                'avg_incap_time': 42.0,
                'tele_cp_rotation_successes': 3,
                'tele_cp_position_successes': 3,
                'climb_all_attempts': 3,
                'matches_played': 3
            },
        ]
        self.test_server.db.insert_documents('obj_tim', obj_tims)
        self.test_calc.run()
        result = self.test_server.db.find('obj_team')
        assert len(result) == 2
        for document in result:
            del document['_id']
            assert document in expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            expected_results.remove(document)
