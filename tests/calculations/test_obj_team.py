#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
from cmath import exp
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
        assert self.test_calc.watched_collections == ["obj_tim", "subj_tim"]
        assert self.test_calc.server == self.test_server

    def test_averages(self):
        """Tests calculate_averages function from src/calculations/obj_team.py"""
        tims = [
            {
                "match_number": 2,
                "auto_hub_highs": 9,
                "auto_launchpad_highs": 0,
                "auto_other_highs": 4,
                "auto_lows": 4,
                "tele_hub_highs": 0,
                "tele_launchpad_highs": 7,
                "tele_other_highs": 2,
                "tele_lows": 16,
                "auto_balls_high": 20,
                "auto_balls_total": 27,
                "tele_balls_high": 24,
                "tele_balls_total": 20,
                "incap": 4,
                "intakes": 51,
                "exit_ball_catches": 0,
                "opp_balls_scored": 1,
            },
            {
                "match_number": 4,
                "auto_hub_highs": 4,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 6,
                "auto_lows": 6,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 3,
                "tele_other_highs": 8,
                "tele_lows": 20,
                "auto_balls_high": 9,
                "auto_balls_total": 22,
                "tele_balls_high": 16,
                "tele_balls_total": 1,
                "incap": 0,
                "intakes": 40,
                "exit_ball_catches": 0,
                "opp_balls_scored": 0,
            },
            {
                "match_number": 5,
                "auto_hub_highs": 9,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 4,
                "auto_lows": 9,
                "tele_hub_highs": 0,
                "tele_launchpad_highs": 3,
                "tele_other_highs": 4,
                "tele_lows": 9,
                "auto_balls_high": 12,
                "auto_balls_total": 5,
                "tele_balls_high": 23,
                "tele_balls_total": 19,
                "incap": 3,
                "intakes": 55,
                "exit_ball_catches": 3,
                "opp_balls_scored": 0,
            },
            {
                "match_number": 3,
                "auto_hub_highs": 0,
                "auto_launchpad_highs": 3,
                "auto_other_highs": 9,
                "auto_lows": 1,
                "tele_hub_highs": 9,
                "tele_launchpad_highs": 4,
                "tele_other_highs": 7,
                "tele_lows": 9,
                "auto_balls_high": 8,
                "auto_balls_total": 13,
                "tele_balls_high": 5,
                "tele_balls_total": 9,
                "incap": 0,
                "intakes": 39,
                "exit_ball_catches": 0,
                "opp_balls_scored": 4,
            },
            {
                "match_number": 1,
                "auto_hub_highs": 1,
                "auto_launchpad_highs": 5,
                "auto_other_highs": 6,
                "auto_lows": 11,
                "tele_hub_highs": 0,
                "tele_launchpad_highs": 9,
                "tele_other_highs": 6,
                "tele_lows": 14,
                "auto_balls_high": 14,
                "auto_balls_total": 17,
                "tele_balls_high": 20,
                "tele_balls_total": 31,
                "incap": 8,
                "intakes": 34,
                "exit_ball_catches": 2,
                "opp_balls_scored": 0,
            },
        ]

        expected_output = {
            "auto_avg_hub_highs": 4.6,
            "auto_avg_launchpad_highs": 2.4,
            "auto_avg_other_highs": 5.8,
            "auto_avg_lows": 6.2,
            "tele_avg_hub_highs": 2.4,
            "tele_avg_launchpad_highs": 5.2,
            "tele_avg_other_highs": 5.4,
            "tele_avg_lows": 13.6,
            "auto_avg_balls_high": 12.6,
            "auto_avg_balls_total": 16.8,
            "tele_avg_balls_high": 17.6,
            "tele_avg_balls_total": 16.0,
            "avg_incap_time": 3.0,
            "avg_intakes": 43.8,
            "avg_exit_ball_catches": 1.0,
            "avg_opp_balls_scored": 1.0,
            "lfm_auto_avg_hub_highs": 5.5,
            "lfm_auto_avg_launchpad_highs": 1.75,
            "lfm_auto_avg_other_highs": 5.75,
            "lfm_auto_avg_lows": 5.0,
            "lfm_tele_avg_hub_highs": 3.0,
            "lfm_tele_avg_launchpad_highs": 4.25,
            "lfm_tele_avg_other_highs": 5.25,
            "lfm_tele_avg_lows": 13.5,
            "lfm_auto_avg_balls_high": 12.25,
            "lfm_tele_avg_balls_high": 17.0,
            "lfm_avg_incap_time": 1.75,
            "lfm_avg_exit_ball_catches": 0.75,
            "lfm_avg_opp_balls_scored": 1.25,
        }
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]
        action_counts = self.test_calc.get_action_counts(tims)
        lfm_action_counts = self.test_calc.get_action_counts(lfm_tims)
        assert (
            self.test_calc.calculate_averages(action_counts, lfm_action_counts)
            == expected_output
        )

    def test_standard_deviations(self):
        """Tests calculate_standard_deviations function from src/calculations/obj_team.py"""
        tims = [
            {
                "match_number": 1,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 1,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 3,
                "auto_balls_high": 2,
                "auto_balls_total": 7,
                "tele_balls_high": 4,
                "tele_balls_total": 2,
                "intakes": 5,
                "incap": 8,
                "exit_ball_catches": 2,
                "opp_balls_scored": 0,
            },
            {
                "match_number": 2,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 5,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 7,
                "auto_balls_high": 6,
                "auto_balls_total": 1,
                "tele_balls_high": 8,
                "tele_balls_total": 6,
                "intakes": 5,
                "incap": 8,
                "exit_ball_catches": 2,
                "opp_balls_scored": 0,
            },
            {
                "match_number": 3,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 19,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 11,
                "auto_balls_high": 10,
                "auto_balls_total": 8,
                "tele_balls_high": 12,
                "tele_balls_total": 3,
                "intakes": 5,
                "incap": 8,
                "exit_ball_catches": 2,
                "opp_balls_scored": 0,
            },
        ]

        expected_output = {
            "auto_sd_balls_low": 7.71722460186015,
            "auto_sd_balls_high": 3.265986323710904,
            "tele_sd_balls_low": 3.265986323710904,
            "tele_sd_balls_high": 3.265986323710904,
        }
        action_counts = self.test_calc.get_action_counts(tims)
        assert (
            self.test_calc.calculate_standard_deviations(action_counts)
            == expected_output
        )

    def test_counts(self):
        """Tests calculate_counts function from src/calculations/obj_team.py"""
        tims = [
            {
                "start_position": "ONE",
                "climb_level": "TRAVERSAL",
                "climb_time": 20,
                "match_number": 1,
                "incap": 2,
            },
            {
                "start_position": "TWO",
                "climb_level": "TRAVERSAL",
                "climb_time": 20,
                "match_number": 4,
                "incap": 0,
            },
            {
                "start_position": "FOUR",
                "climb_level": "NONE",
                "climb_time": 5,
                "match_number": 3,
                "incap": 0,
            },
            {
                "start_position": "ONE",
                "climb_level": "NONE",
                "climb_time": 0,
                "match_number": 2,
                "incap": 0,
            },
            {
                "start_position": "THREE",
                "climb_level": "LOW",
                "climb_time": 5,
                "match_number": 5,
                "incap": 0,
            },
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]

        expected_output = {
            'climb_all_attempts': 4,
            'low_rung_successes': 1,
            'mid_rung_successes': 0,
            'high_rung_successes': 0,
            'traversal_rung_successes': 2,
            'position_zero_starts': 0,
            'position_one_starts': 2,
            'position_two_starts': 1,
            'position_three_starts': 1,
            'position_four_starts': 1,
            'matches_incap': 1,
            'matches_played': 5,
            'lfm_climb_all_attempts': 3,
            'lfm_low_rung_successes': 1,
            'lfm_mid_rung_successes': 0,
            'lfm_high_rung_successes': 0,
            'lfm_traversal_rung_successes': 1,
            'lfm_matches_incap': 0,
        }
        assert self.test_calc.calculate_counts(tims, lfm_tims) == expected_output

    def test_super_counts(self):
        """Tests calculate_super_counts function from src/calculations.obj_team.py"""
        tims = [
            {"match_number": 1, "team_number": 1678, "scored_far": True},
            {
                "match_number": 2,
                "team_number": 1678,
                "scored_far": False,
            },
            {
                "match_number": 3,
                "team_number": 1678,
                "scored_far": True,
            },
        ]
        expected_output = {"matches_scored_far": 2}
        assert self.test_calc.calculate_super_counts(tims) == expected_output

    def test_extrema(self):
        tims = [
            {
                "auto_balls_high": 7,
                "auto_balls_total": 13,
                "tele_balls_high": 9,
                "tele_balls_total": 17,
                "intakes": 10,
                "incap": 11,
                "exit_ball_catches": 12,
                "opp_balls_scored": 0,
                "climb_level": "NONE",
                "match_number": 1,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 6,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 8,
                "start_position": "ONE",
            },
            {
                "auto_balls_high": 2,
                "auto_balls_total": 3,
                "tele_balls_high": 4,
                "tele_balls_total": 7,
                "intakes": 5,
                "incap": 6,
                "exit_ball_catches": 7,
                "opp_balls_scored": 8,
                "climb_level": "NONE",
                "match_number": 2,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 1,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 3,
                "start_position": "ONE",
            },
            {
                "auto_balls_high": 3,
                "auto_balls_total": 5,
                "tele_balls_high": 5,
                "tele_balls_total": 9,
                "intakes": 6,
                "incap": 7,
                "exit_ball_catches": 8,
                "opp_balls_scored": 9,
                "climb_level": "MID",
                "match_number": 3,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 2,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 4,
                "start_position": "ONE",
            },
            {
                "auto_balls_high": 4,
                "auto_balls_total": 7,
                "tele_balls_high": 6,
                "tele_balls_total": 11,
                "intakes": 7,
                "incap": 8,
                "exit_ball_catches": 9,
                "opp_balls_scored": 10,
                "climb_level": "LOW",
                "match_number": 4,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 3,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 5,
                "start_position": "ONE",
            },
            {
                "auto_balls_high": 5,
                "auto_balls_total": 9,
                "tele_balls_high": 7,
                "tele_balls_total": 13,
                "intakes": 8,
                "incap": 9,
                "exit_ball_catches": 10,
                "opp_balls_scored": 11,
                "climb_level": "HIGH",
                "match_number": 5,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 2,
                "auto_other_highs": 5,
                "auto_lows": 4,
                "tele_hub_highs": 3,
                "tele_launchpad_highs": 2,
                "tele_other_highs": 5,
                "tele_lows": 6,
                "start_position": "ONE",
            },
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]
        action_counts = self.test_calc.get_action_counts(tims)
        lfm_action_counts = self.test_calc.get_action_counts(lfm_tims)
        action_categories = self.test_calc.get_action_categories(tims)
        lfm_action_categories = self.test_calc.get_action_categories(lfm_tims)
        expected_output = {
            "auto_max_balls_low": 6,
            "auto_max_balls_high": 7,
            "tele_max_balls_low": 8,
            "tele_max_balls_high": 9,
            "max_incap": 11,
            "max_exit_ball_catches": 12,
            "max_opp_balls_scored": 11,
            "max_climb_level": "HIGH",
            "lfm_auto_max_balls_low": 4,
            "lfm_auto_max_balls_high": 5,
            "lfm_tele_max_balls_low": 6,
            "lfm_tele_max_balls_high": 7,
            "lfm_max_incap": 9,
            "lfm_max_exit_ball_catches": 10,
            "lfm_max_opp_balls_scored": 11,
            "lfm_max_climb_level": "HIGH",
        }
        assert (
            self.test_calc.calculate_extrema(
                action_counts,
                lfm_action_counts,
                action_categories,
                lfm_action_categories,
            )
            == expected_output
        )

    def test_modes(self):
        tims = [
            {'match_number': 1, 'climb_level': 'LOW', 'start_position': 'ONE'},
            {'match_number': 2, 'climb_level': 'LOW', 'start_position': 'TWO'},
            {'match_number': 3, 'climb_level': 'MID', 'start_position': 'THREE'},
            {'match_number': 4, 'climb_level': 'TRAVERSAL', 'start_position': 'ONE'},
            {'match_number': 5, 'climb_level': 'HIGH', 'start_position': 'TWO'},
            {'match_number': 6, 'climb_level': 'MID', 'start_position': 'THREE'},
            {'match_number': 7, 'climb_level': 'LOW', 'start_position': 'ZERO'},
            {'match_number': 8, 'climb_level': 'LOW', 'start_position': 'ZERO'},
            {'match_number': 9, 'climb_level': 'TRAVERSAL', 'start_position': 'ZERO'},
            {'match_number': 10, 'climb_level': 'LOW', 'start_position': 'ZERO'},
            {'match_number': 11, 'climb_level': 'HIGH', 'start_position': 'ZERO'},
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 2]
        action_categories = self.test_calc.get_action_categories(tims)
        lfm_action_categories = self.test_calc.get_action_categories(lfm_tims)
        assert self.test_calc.calculate_modes(
            action_categories, lfm_action_categories
        ) == {
            "mode_climb_level": ["LOW"],
            "mode_start_position": ["ONE", "TWO", "THREE"],
            "lfm_mode_start_position": ["THREE"],
        }

    def test_climb_times(self):
        tims = [
            {"match_number": 1, "climb_level": "LOW", "climb_time": 8},
            {"match_number": 2, "climb_level": "LOW", "climb_time": 9},
            {"match_number": 3, "climb_level": "MID", "climb_time": 20},
            {"match_number": 4, "climb_level": "HIGH", "climb_time": 13},
            {"match_number": 5, "climb_level": "LOW", "climb_time": 2},
            {"match_number": 6, "climb_level": "HIGH", "climb_time": 10},
            {"match_number": 7, "climb_level": "LOW", "climb_time": 4},
            {"match_number": 8, "climb_level": "NONE", "climb_time": 9},
        ]
        expected_results = {
            "low_avg_time": 5.75,
            "mid_avg_time": 20.0,
            "high_avg_time": 11.5,
            "traversal_avg_time": 0.0,
            "lfm_low_avg_time": 3.0,
            "lfm_mid_avg_time": 0.0,
            "lfm_high_avg_time": 10.0,
            "lfm_traversal_avg_time": 0.0,
        }
        lfm_tims = [tim for tim in tims if tim["match_number"] > 4]
        successful_climb_times = self.test_calc.get_climb_times(tims)
        lfm_successful_climb_times = self.test_calc.get_climb_times(lfm_tims)
        assert (
            self.test_calc.calculate_climb_times(
                successful_climb_times, lfm_successful_climb_times
            )
            == expected_results
        )

    def test_success_rates(self):
        team_data = {
            "climb_all_attempts": 4,
            "low_rung_successes": 1,
            "mid_rung_successes": 0,
            "high_rung_successes": 0,
            "traversal_rung_successes": 2,
            "lfm_climb_all_attempts": 3,
            "lfm_low_rung_successes": 1,
            "lfm_mid_rung_successes": 0,
            "lfm_high_rung_successes": 0,
            "lfm_traversal_rung_successes": 1,
        }
        assert self.test_calc.calculate_success_rates(team_data) == {
            "climb_percent_success": 0.75,
            "lfm_climb_percent_success": 0.6666666666666666,
        }

    def test_calculate_average_points(self):
        team_data = {
            "low_rung_successes": 2,
            "mid_rung_successes": 1,
            "high_rung_successes": 1,
            "traversal_rung_successes": 4,
        }
        assert self.test_calc.calculate_average_points(team_data) == {"avg_climb_points": 10.5}

    def test_run(self):
        """Tests run function from src/calculations/obj_team.py"""
        subj_tims = [
            {
                "match_number": 1,
                "team_number": 973,
                "scored_far": True,
            },
            {
                "match_number": 2,
                "team_number": 973,
                "scored_far": True,
            },
            {
                "match_number": 3,
                "team_number": 973,
                "scored_far": False,
            },
            {
                "match_number": 4,
                "team_number": 973,
                "scored_far": True,
            },
            {
                "match_number": 5,
                "team_number": 973,
                "scored_far": True,
            },
            {
                "match_number": 1,
                "team_number": 1678,
                "scored_far": False,
            },
            {
                "match_number": 2,
                "team_number": 1678,
                "scored_far": True,
            },
            {
                "match_number": 3,
                "team_number": 1678,
                "scored_far": False,
            },
            {
                "match_number": 4,
                "team_number": 1678,
                "scored_far": True,
            },
            {
                "match_number": 5,
                "team_number": 1678,
                "scored_far": False,
            },
        ]
        obj_tims = [
            # 973
            {
                "match_number": 1,
                "auto_balls_high": 61,
                "auto_balls_total": 127,
                "tele_balls_high": 45,
                "tele_balls_total": 63,
                "incap": 14,
                "confidence_rating": 30,
                "team_number": 973,
                "auto_hub_highs": 1,
                "auto_launchpad_highs": 3,
                "auto_other_highs": 4,
                "auto_lows": 66,
                "tele_hub_highs": 8,
                "tele_launchpad_highs": 10,
                "tele_other_highs": 11,
                "tele_lows": 18,
                "intakes": 15,
                "exit_ball_catches": 16,
                "opp_balls_scored": 17,
                "climb_time": 18,
                "climb_level": "LOW",
                "start_position": "ONE",
            },
            {
                "match_number": 2,
                "auto_balls_high": 60,
                "auto_balls_total": 90,
                "tele_balls_high": 1,
                "tele_balls_total": 57,
                "incap": 22,
                "confidence_rating": 68,
                "team_number": 973,
                "auto_hub_highs": 2,
                "auto_launchpad_highs": 4,
                "auto_other_highs": 5,
                "auto_lows": 30,
                "tele_hub_highs": 9,
                "tele_launchpad_highs": 11,
                "tele_other_highs": 12,
                "tele_lows": 56,
                "intakes": 16,
                "exit_ball_catches": 17,
                "opp_balls_scored": 18,
                "climb_time": 19,
                "climb_level": "NONE",
                "start_position": "TWO",
            },
            {
                "match_number": 3,
                "auto_balls_high": 92,
                "auto_balls_total": 176,
                "tele_balls_high": 68,
                "tele_balls_total": 108,
                "incap": 18,
                "confidence_rating": 2,
                "team_number": 973,
                "auto_hub_highs": 3,
                "auto_launchpad_highs": 5,
                "auto_other_highs": 6,
                "auto_lows": 84,
                "tele_hub_highs": 10,
                "tele_launchpad_highs": 12,
                "tele_other_highs": 13,
                "tele_lows": 40,
                "intakes": 17,
                "exit_ball_catches": 18,
                "opp_balls_scored": 19,
                "climb_time": 20,
                "climb_level": "HIGH",
                "start_position": "FOUR",
            },
            # 1678
            {
                "match_number": 1,
                "auto_balls_high": 76,
                "auto_balls_total": 123,
                "tele_balls_high": 81,
                "tele_balls_total": 115,
                "incap": 17,
                "confidence_rating": 31,
                "team_number": 1678,
                "auto_hub_highs": 4,
                "auto_launchpad_highs": 6,
                "auto_other_highs": 7,
                "auto_lows": 47,
                "tele_hub_highs": 11,
                "tele_launchpad_highs": 13,
                "tele_other_highs": 14,
                "tele_lows": 34,
                "intakes": 18,
                "exit_ball_catches": 19,
                "opp_balls_scored": 20,
                "climb_time": 21,
                "climb_level": "TRAVERSAL",
                "start_position": "THREE",
            },
            {
                "match_number": 2,
                "auto_balls_high": 54,
                "auto_balls_total": 79,
                "tele_balls_high": 59,
                "tele_balls_total": 140,
                "incap": 93,
                "climb_time": 35,
                "confidence_rating": 14,
                "team_number": 1678,
                "auto_hub_highs": 5,
                "auto_launchpad_highs": 7,
                "auto_other_highs": 8,
                "auto_lows": 25,
                "tele_hub_highs": 12,
                "tele_launchpad_highs": 14,
                "tele_other_highs": 15,
                "tele_lows": 81,
                "intakes": 19,
                "exit_ball_catches": 20,
                "opp_balls_scored": 21,
                "climb_time": 22,
                "climb_level": "LOW",
                "start_position": "FOUR",
            },
            {
                "match_number": 3,
                "auto_balls_high": 50,
                "auto_balls_total": 104,
                "tele_balls_high": 73,
                "tele_balls_total": 162,
                "incap": 16,
                "climb_time": 97,
                "confidence_rating": 77,
                "team_number": 1678,
                "auto_hub_highs": 7,
                "auto_launchpad_highs": 9,
                "auto_other_highs": 10,
                "auto_lows": 54,
                "tele_hub_highs": 14,
                "tele_launchpad_highs": 16,
                "tele_other_highs": 17,
                "tele_lows": 89,
                "intakes": 21,
                "exit_ball_catches": 22,
                "opp_balls_scored": 23,
                "climb_time": 24,
                "climb_level": "LOW",
                "start_position": "FOUR",
            },
            {
                "match_number": 4,
                "auto_balls_high": 2,
                "auto_balls_total": 3,
                "tele_balls_high": 4,
                "tele_balls_total": 7,
                "incap": 5,
                "climb_time": 6,
                "confidence_rating": 7,
                "team_number": 1678,
                "auto_hub_highs": 8,
                "auto_launchpad_highs": 10,
                "auto_other_highs": 11,
                "auto_lows": 1,
                "tele_hub_highs": 15,
                "tele_launchpad_highs": 17,
                "tele_other_highs": 18,
                "tele_lows": 3,
                "intakes": 22,
                "exit_ball_catches": 23,
                "opp_balls_scored": 24,
                "climb_time": 25,
                "climb_level": "MID",
                "start_position": "FOUR",
            },
            {
                "match_number": 5,
                "auto_balls_high": 3,
                "auto_balls_total": 5,
                "tele_balls_high": 5,
                "tele_balls_total": 9,
                "incap": 6,
                "climb_time": 7,
                "confidence_rating": 8,
                "team_number": 1678,
                "auto_hub_highs": 9,
                "auto_launchpad_highs": 11,
                "auto_other_highs": 12,
                "auto_lows": 2,
                "tele_hub_highs": 16,
                "tele_launchpad_highs": 18,
                "tele_other_highs": 19,
                "tele_lows": 4,
                "intakes": 23,
                "exit_ball_catches": 24,
                "opp_balls_scored": 25,
                "climb_time": 26,
                "climb_level": "LOW",
                "start_position": "ONE",
            },
        ]
        expected_results = [
            {
                "team_number": 973,
                # Averages
                "auto_avg_hub_highs": 2.0,
                "auto_avg_launchpad_highs": 4.0,
                "auto_avg_other_highs": 5.0,
                "auto_avg_lows": 60.0,
                "tele_avg_hub_highs": 9.0,
                "tele_avg_launchpad_highs": 11.0,
                "tele_avg_other_highs": 12.0,
                "tele_avg_lows": 38.0,
                "avg_intakes": 16.0,
                "avg_exit_ball_catches": 17.0,
                "avg_opp_balls_scored": 18.0,
                "auto_avg_balls_total": 131.0,
                "tele_avg_balls_total": 76.0,
                "auto_avg_balls_high": 71.0,
                "tele_avg_balls_high": 38.0,
                "avg_incap_time": 18.0,
                # LFM Averages
                "lfm_auto_avg_hub_highs": 2.0,
                "lfm_auto_avg_launchpad_highs": 4.0,
                "lfm_auto_avg_other_highs": 5.0,
                "lfm_auto_avg_lows": 60.0,
                "lfm_tele_avg_hub_highs": 9.0,
                "lfm_tele_avg_launchpad_highs": 11.0,
                "lfm_tele_avg_other_highs": 12.0,
                "lfm_tele_avg_lows": 38.0,
                "lfm_avg_exit_ball_catches": 17.0,
                "lfm_avg_opp_balls_scored": 18.0,
                "lfm_auto_avg_balls_high": 71.0,
                "lfm_tele_avg_balls_high": 38.0,
                "lfm_avg_incap_time": 18.0,
                # Standard Deviations
                "auto_sd_balls_low": 22.44994432064365,
                "auto_sd_balls_high": 14.854853303438128,
                "tele_sd_balls_low": 15.57776192739723,
                "tele_sd_balls_high": 27.796882319185844,
                # Counts
                'matches_played': 3,
                'climb_all_attempts': 3,
                'low_rung_successes': 1,
                'mid_rung_successes': 0,
                'high_rung_successes': 1,
                'traversal_rung_successes': 0,
                'position_zero_starts': 0,
                'position_one_starts': 1,
                'position_two_starts': 1,
                'position_three_starts': 0,
                'position_four_starts': 1,
                'matches_incap': 3,
                # LFM Counts
                "lfm_climb_all_attempts": 3,
                "lfm_low_rung_successes": 1,
                "lfm_mid_rung_successes": 0,
                "lfm_high_rung_successes": 1,
                "lfm_traversal_rung_successes": 0,
                "lfm_matches_incap": 3,
                # Super Counts
                "matches_scored_far": 4,
                # Extrema
                "auto_max_balls_low": 84,
                "auto_max_balls_high": 92,
                "tele_max_balls_low": 56,
                "tele_max_balls_high": 68,
                "max_exit_ball_catches": 18,
                "max_opp_balls_scored": 19,
                "max_incap": 22,
                "max_climb_level": "HIGH",
                # LFM Extrema
                "lfm_auto_max_balls_low": 84,
                "lfm_auto_max_balls_high": 92,
                "lfm_tele_max_balls_low": 56,
                "lfm_tele_max_balls_high": 68,
                "lfm_max_exit_ball_catches": 18,
                "lfm_max_opp_balls_scored": 19,
                "lfm_max_incap": 22,
                "lfm_max_climb_level": "HIGH",
                # Modes
                "mode_climb_level": ["LOW", "NONE", "HIGH"],
                "mode_start_position": ["ONE", "TWO", "FOUR"],
                # LFM Modes
                "lfm_mode_start_position": ["ONE", "TWO", "FOUR"],
                # Climb Times
                "low_avg_time": 18.0,
                "mid_avg_time": 0.0,
                "high_avg_time": 20.0,
                "traversal_avg_time": 0.0,
                # LFM Climb times
                "lfm_low_avg_time": 18.0,
                "lfm_mid_avg_time": 0.0,
                "lfm_high_avg_time": 20.0,
                "lfm_traversal_avg_time": 0.0,
                # Success Rates
                "climb_percent_success": 0.6666666666666666,
                # LFM Success Rates
                "lfm_climb_percent_success": 0.6666666666666666,
                # Average Points
                "avg_climb_points": 7,
            },
            {
                "team_number": 1678,
                # Averages
                "auto_avg_hub_highs": 6.6,
                "auto_avg_launchpad_highs": 8.6,
                "auto_avg_other_highs": 9.6,
                "auto_avg_lows": 25.8,
                "tele_avg_hub_highs": 13.6,
                "tele_avg_launchpad_highs": 15.6,
                "tele_avg_other_highs": 16.6,
                "tele_avg_lows": 42.2,
                "avg_intakes": 20.6,
                "avg_exit_ball_catches": 21.6,
                "avg_opp_balls_scored": 22.6,
                "auto_avg_balls_total": 62.8,
                "tele_avg_balls_total": 86.6,
                "auto_avg_balls_high": 37.0,
                "tele_avg_balls_high": 44.4,
                "avg_incap_time": 27.4,
                # LFM Averages
                "lfm_auto_avg_hub_highs": 7.25,
                "lfm_auto_avg_launchpad_highs": 9.25,
                "lfm_auto_avg_other_highs": 10.25,
                "lfm_auto_avg_lows": 20.5,
                "lfm_tele_avg_hub_highs": 14.25,
                "lfm_tele_avg_launchpad_highs": 16.25,
                "lfm_tele_avg_other_highs": 17.25,
                "lfm_tele_avg_lows": 44.25,
                "lfm_avg_exit_ball_catches": 22.25,
                "lfm_avg_opp_balls_scored": 23.25,
                "lfm_auto_avg_balls_high": 27.25,
                "lfm_tele_avg_balls_high": 35.25,
                "lfm_avg_incap_time": 30.0,
                # Standard Deviations
                "auto_sd_balls_low": 22.03088740836374,
                "auto_sd_balls_high": 29.5296461204668,
                "tele_sd_balls_low": 36.766288907095316,
                "tele_sd_balls_high": 33.332266649599454,
                # Counts
                'matches_played': 5,
                'climb_all_attempts': 5,
                'low_rung_successes': 3,
                'mid_rung_successes': 1,
                'high_rung_successes': 0,
                'traversal_rung_successes': 1,
                'position_zero_starts': 0,
                'position_one_starts': 1,
                'position_two_starts': 0,
                'position_three_starts': 1,
                'position_four_starts': 3,
                'matches_incap': 5,
                # LFM Counts
                "lfm_climb_all_attempts": 4,
                "lfm_low_rung_successes": 3,
                "lfm_mid_rung_successes": 1,
                "lfm_high_rung_successes": 0,
                "lfm_traversal_rung_successes": 0,
                "lfm_matches_incap": 4,
                # Super Counts
                "matches_scored_far": 2,
                # Extrema
                "auto_max_balls_low": 54,
                "auto_max_balls_high": 76,
                "tele_max_balls_low": 89,
                "tele_max_balls_high": 81,
                "max_incap": 93,
                "max_exit_ball_catches": 24,
                "max_opp_balls_scored": 25,
                "max_climb_level": "TRAVERSAL",
                # LFM Extrema
                "lfm_auto_max_balls_low": 54,
                "lfm_auto_max_balls_high": 54,
                "lfm_tele_max_balls_low": 89,
                "lfm_tele_max_balls_high": 73,
                "lfm_max_incap": 93,
                "lfm_max_exit_ball_catches": 24,
                "lfm_max_opp_balls_scored": 25,
                "lfm_max_climb_level": "MID",
                # Modes
                "mode_climb_level": ["LOW"],
                "mode_start_position": ["FOUR"],
                # LFM Modes
                "lfm_mode_start_position": ["FOUR"],
                # Climb Times
                "low_avg_time": 24.0,
                "mid_avg_time": 25.0,
                "high_avg_time": 0.0,
                "traversal_avg_time": 21.0,
                # LFM Climb Times
                "lfm_low_avg_time": 24.0,
                "lfm_mid_avg_time": 25.0,
                "lfm_high_avg_time": 0.0,
                "lfm_traversal_avg_time": 0.0,
                # Success Rates
                "climb_percent_success": 1.0,
                # LFM Success Rates
                "lfm_climb_percent_success": 1.0,
                # Average Points
                "avg_climb_points": 6.6,
            },
        ]
        self.test_server.db.insert_documents("obj_tim", obj_tims)
        self.test_server.db.insert_documents("subj_tim", subj_tims)
        self.test_calc.run()
        result = self.test_server.db.find("obj_team")
        assert len(result) == 2
        for document in result:
            del document["_id"]
            assert document in expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            expected_results.remove(document)
