#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
from cmath import exp
import pytest
from unittest.mock import patch
from calculations import obj_team
from server import Server


@pytest.mark.clouddb
class TestOBJTeamCalc:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
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
                "auto_low_balls": 4,
                "tele_low_balls": 16,
                "auto_high_balls": 20,
                "auto_total_balls": 27,
                "tele_high_balls": 24,
                "tele_total_balls": 20,
                "incap": 4,
                "intakes": 51,
            },
            {
                "match_number": 4,
                "auto_low_balls": 6,
                "tele_low_balls": 20,
                "auto_high_balls": 9,
                "auto_total_balls": 22,
                "tele_high_balls": 16,
                "tele_total_balls": 1,
                "incap": 0,
                "intakes": 40,
            },
            {
                "match_number": 5,
                "auto_low_balls": 9,
                "tele_low_balls": 9,
                "auto_high_balls": 12,
                "auto_total_balls": 5,
                "tele_high_balls": 23,
                "tele_total_balls": 19,
                "incap": 3,
                "intakes": 55,
            },
            {
                "match_number": 3,
                "auto_low_balls": 1,
                "tele_low_balls": 9,
                "auto_high_balls": 8,
                "auto_total_balls": 13,
                "tele_high_balls": 5,
                "tele_total_balls": 9,
                "incap": 0,
                "intakes": 39,
            },
            {
                "match_number": 1,
                "auto_low_balls": 11,
                "tele_low_balls": 14,
                "auto_high_balls": 14,
                "auto_total_balls": 17,
                "tele_high_balls": 20,
                "tele_total_balls": 31,
                "incap": 8,
                "intakes": 34,
            },
        ]

        expected_output = {
            "auto_avg_low_balls": 6.2,
            "tele_avg_low_balls": 13.6,
            "auto_avg_high_balls": 12.6,
            "auto_avg_total_balls": 16.8,
            "tele_avg_high_balls": 17.6,
            "tele_avg_total_balls": 16.0,
            "avg_incap_time": 3.0,
            "avg_intakes": 43.8,
            "lfm_auto_avg_low_balls": 5.0,
            "lfm_tele_avg_low_balls": 13.5,
            "lfm_auto_avg_high_balls": 12.25,
            "lfm_tele_avg_high_balls": 17.0,
            "lfm_avg_incap_time": 1.75,
        }
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]
        action_counts = self.test_calc.get_action_counts(tims)
        lfm_action_counts = self.test_calc.get_action_counts(lfm_tims)
        assert (
            self.test_calc.calculate_averages(action_counts, lfm_action_counts) == expected_output
        )

    def test_standard_deviations(self):
        """Tests calculate_standard_deviations function from src/calculations/obj_team.py"""
        tims = [
            {
                "match_number": 1,
                "auto_high_balls": 2,
                "auto_low_balls": 1,
                "auto_total_balls": 7,
                "tele_high_balls": 4,
                "tele_low_balls": 3,
                "tele_total_balls": 2,
                "intakes": 5,
                "incap": 8,
            },
            {
                "match_number": 2,
                "auto_high_balls": 6,
                "auto_low_balls": 5,
                "auto_total_balls": 1,
                "tele_high_balls": 8,
                "tele_low_balls": 7,
                "tele_total_balls": 6,
                "intakes": 5,
                "incap": 8,
            },
            {
                "match_number": 3,
                "auto_high_balls": 10,
                "auto_low_balls": 19,
                "auto_total_balls": 8,
                "tele_high_balls": 12,
                "tele_low_balls": 11,
                "tele_total_balls": 3,
                "intakes": 5,
                "incap": 8,
            },
        ]

        expected_output = {
            "auto_sd_low_balls": 7.71722460186015,
            "auto_sd_high_balls": 3.265986323710904,
            "tele_sd_low_balls": 3.265986323710904,
            "tele_sd_high_balls": 3.265986323710904,
        }
        action_counts = self.test_calc.get_action_counts(tims)
        assert self.test_calc.calculate_standard_deviations(action_counts) == expected_output

    def test_counts(self):
        """Tests calculate_counts function from src/calculations/obj_team.py"""
        tims = [
            {
                "start_position": "ONE",
                "climb_level": "TRAVERSAL",
                "climb_attempts": 1,
                "match_number": 1,
                "incap": 2,
            },
            {
                "start_position": "TWO",
                "climb_level": "TRAVERSAL",
                "climb_attempts": 1,
                "match_number": 4,
                "incap": 0,
            },
            {
                "start_position": "FOUR",
                "climb_level": "NONE",
                # Even if a team has multiple attempts in a match, only one is counted for each match
                "climb_attempts": 6,
                "match_number": 3,
                "incap": 0,
            },
            {
                "start_position": "ONE",
                "climb_level": "NONE",
                "climb_attempts": 0,
                "match_number": 2,
                "incap": 0,
            },
            {
                "start_position": "THREE",
                "climb_level": "LOW",
                "climb_attempts": 0,
                "match_number": 5,
                "incap": 0,
            },
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]

        expected_output = {
            "climb_all_attempts": 3,
            "low_rung_successes": 1,
            "mid_rung_successes": 0,
            "high_rung_successes": 0,
            "traversal_rung_successes": 2,
            "position_zero_starts": 0,
            "position_one_starts": 2,
            "position_two_starts": 1,
            "position_three_starts": 1,
            "position_four_starts": 1,
            "matches_incap": 1,
            "matches_played": 5,
            "lfm_climb_all_attempts": 2,
            "lfm_low_rung_successes": 1,
            "lfm_mid_rung_successes": 0,
            "lfm_high_rung_successes": 0,
            "lfm_traversal_rung_successes": 1,
            "lfm_matches_incap": 0,
        }
        assert self.test_calc.calculate_counts(tims, lfm_tims) == expected_output

    def test_super_counts(self):
        """Tests calculate_super_counts function from src/calculations.obj_team.py"""
        tims = [
            {"match_number": 1, "team_number": "1678", "played_defense": True},
            {
                "match_number": 2,
                "team_number": "1678",
                "played_defense": False,
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "played_defense": True,
            },
        ]
        expected_output = {"matches_played_defense": 2}
        assert self.test_calc.calculate_super_counts(tims) == expected_output

    def test_extrema(self):
        tims = [
            {
                "auto_high_balls": 7,
                "auto_low_balls": 6,
                "auto_total_balls": 13,
                "tele_high_balls": 9,
                "tele_low_balls": 8,
                "tele_total_balls": 17,
                "intakes": 10,
                "incap": 11,
                "climb_level": "NONE",
                "match_number": 1,
                "start_position": "ONE",
            },
            {
                "auto_high_balls": 2,
                "auto_low_balls": 1,
                "auto_total_balls": 3,
                "tele_high_balls": 4,
                "tele_low_balls": 3,
                "tele_total_balls": 7,
                "intakes": 5,
                "incap": 6,
                "climb_level": "NONE",
                "match_number": 2,
                "start_position": "ONE",
            },
            {
                "auto_high_balls": 3,
                "auto_low_balls": 2,
                "auto_total_balls": 5,
                "tele_high_balls": 5,
                "tele_low_balls": 4,
                "tele_total_balls": 9,
                "intakes": 6,
                "incap": 7,
                "climb_level": "MID",
                "match_number": 3,
                "start_position": "ONE",
            },
            {
                "auto_high_balls": 4,
                "auto_low_balls": 3,
                "auto_total_balls": 7,
                "tele_low_balls": 5,
                "tele_high_balls": 6,
                "tele_total_balls": 11,
                "intakes": 7,
                "incap": 8,
                "climb_level": "LOW",
                "match_number": 4,
                "start_position": "ONE",
            },
            {
                "auto_high_balls": 5,
                "auto_low_balls": 4,
                "auto_total_balls": 9,
                "tele_high_balls": 7,
                "tele_low_balls": 6,
                "tele_total_balls": 13,
                "intakes": 8,
                "incap": 9,
                "climb_level": "HIGH",
                "match_number": 5,
                "start_position": "ONE",
            },
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 1]
        action_counts = self.test_calc.get_action_counts(tims)
        lfm_action_counts = self.test_calc.get_action_counts(lfm_tims)
        action_categories = self.test_calc.get_action_categories(tims)
        lfm_action_categories = self.test_calc.get_action_categories(lfm_tims)
        expected_output = {
            "auto_max_low_balls": 6,
            "auto_max_high_balls": 7,
            "tele_max_low_balls": 8,
            "tele_max_high_balls": 9,
            "max_incap": 11,
            "max_climb_level": "HIGH",
            "lfm_auto_max_low_balls": 4,
            "lfm_auto_max_high_balls": 5,
            "lfm_tele_max_low_balls": 6,
            "lfm_tele_max_high_balls": 7,
            "lfm_max_incap": 9,
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
            {"match_number": 1, "climb_level": "LOW", "start_position": "ONE"},
            {"match_number": 2, "climb_level": "LOW", "start_position": "TWO"},
            {"match_number": 3, "climb_level": "MID", "start_position": "THREE"},
            {"match_number": 4, "climb_level": "TRAVERSAL", "start_position": "ONE"},
            {"match_number": 5, "climb_level": "HIGH", "start_position": "TWO"},
            {"match_number": 6, "climb_level": "MID", "start_position": "THREE"},
            {"match_number": 7, "climb_level": "LOW", "start_position": "ZERO"},
            {"match_number": 8, "climb_level": "LOW", "start_position": "ZERO"},
            {"match_number": 9, "climb_level": "TRAVERSAL", "start_position": "ZERO"},
            {"match_number": 10, "climb_level": "LOW", "start_position": "ZERO"},
            {"match_number": 11, "climb_level": "HIGH", "start_position": "ZERO"},
        ]
        lfm_tims = [tim for tim in tims if tim["match_number"] > 2]
        action_categories = self.test_calc.get_action_categories(tims)
        lfm_action_categories = self.test_calc.get_action_categories(lfm_tims)
        assert self.test_calc.calculate_modes(action_categories, lfm_action_categories) == {
            "mode_climb_level": ["LOW"],
            "mode_start_position": ["ONE", "TWO", "THREE"],
            "lfm_mode_start_position": ["THREE"],
        }

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
                "team_number": "973",
                "played_defense": True,
            },
            {
                "match_number": 2,
                "team_number": "973",
                "played_defense": True,
            },
            {
                "match_number": 3,
                "team_number": "973",
                "played_defense": False,
            },
            {
                "match_number": 4,
                "team_number": "973",
                "played_defense": True,
            },
            {
                "match_number": 5,
                "team_number": "973",
                "played_defense": True,
            },
            {
                "match_number": 1,
                "team_number": "1678",
                "played_defense": False,
            },
            {
                "match_number": 2,
                "team_number": "1678",
                "played_defense": True,
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "played_defense": False,
            },
            {
                "match_number": 4,
                "team_number": "1678",
                "played_defense": True,
            },
            {
                "match_number": 5,
                "team_number": "1678",
                "played_defense": False,
            },
        ]
        obj_tims = [
            # 973
            {
                "match_number": 1,
                "auto_high_balls": 61,
                "auto_low_balls": 66,
                "auto_total_balls": 127,
                "tele_low_balls": 18,
                "tele_high_balls": 45,
                "tele_total_balls": 63,
                "incap": 14,
                "confidence_rating": 30,
                "team_number": "973",
                "climb_attempts": 1,
                "intakes": 15,
                "climb_level": "LOW",
                "start_position": "ONE",
            },
            {
                "match_number": 2,
                "auto_high_balls": 60,
                "auto_low_balls": 30,
                "auto_total_balls": 90,
                "tele_high_balls": 1,
                "tele_low_balls": 56,
                "tele_total_balls": 57,
                "incap": 22,
                "confidence_rating": 68,
                "team_number": "973",
                "climb_attempts": 1,
                "intakes": 16,
                "climb_level": "NONE",
                "start_position": "TWO",
            },
            {
                "match_number": 3,
                "auto_high_balls": 92,
                "auto_low_balls": 84,
                "" "auto_total_balls": 176,
                "tele_high_balls": 68,
                "tele_low_balls": 40,
                "tele_total_balls": 108,
                "incap": 18,
                "confidence_rating": 2,
                "team_number": "973",
                "climb_attempts": 2,
                "intakes": 17,
                "climb_level": "HIGH",
                "start_position": "FOUR",
            },
            # 1678
            {
                "match_number": 1,
                "auto_high_balls": 76,
                "auto_low_balls": 47,
                "auto_total_balls": 123,
                "tele_high_balls": 81,
                "tele_low_balls": 34,
                "tele_total_balls": 115,
                "incap": 17,
                "confidence_rating": 31,
                "team_number": "1678",
                "climb_attempts": 1,
                "intakes": 18,
                "climb_level": "TRAVERSAL",
                "start_position": "THREE",
            },
            {
                "match_number": 2,
                "auto_high_balls": 54,
                "tele_low_balls": 81,
                "auto_total_balls": 79,
                "tele_high_balls": 59,
                "auto_low_balls": 25,
                "tele_total_balls": 140,
                "incap": 93,
                "confidence_rating": 14,
                "team_number": "1678",
                "climb_attempts": 1,
                "intakes": 19,
                "climb_level": "LOW",
                "start_position": "FOUR",
            },
            {
                "match_number": 3,
                "auto_high_balls": 50,
                "auto_low_balls": 54,
                "auto_total_balls": 104,
                "tele_high_balls": 73,
                "tele_low_balls": 89,
                "tele_total_balls": 162,
                "incap": 16,
                "confidence_rating": 77,
                "team_number": "1678",
                "climb_attempts": 1,
                "intakes": 21,
                "climb_level": "LOW",
                "start_position": "FOUR",
            },
            {
                "match_number": 4,
                "auto_high_balls": 2,
                "auto_low_balls": 1,
                "auto_total_balls": 3,
                "tele_high_balls": 4,
                "tele_low_balls": 3,
                "tele_total_balls": 7,
                "incap": 5,
                "confidence_rating": 7,
                "team_number": "1678",
                "climb_attempts": 1,
                "intakes": 22,
                "climb_level": "MID",
                "start_position": "FOUR",
            },
            {
                "match_number": 5,
                "auto_high_balls": 3,
                "auto_low_balls": 2,
                "auto_total_balls": 5,
                "tele_high_balls": 5,
                "tele_low_balls": 4,
                "tele_total_balls": 9,
                "incap": 6,
                "confidence_rating": 8,
                "team_number": "1678",
                "climb_attempts": 1,
                "intakes": 23,
                "climb_level": "LOW",
                "start_position": "ONE",
            },
        ]
        expected_results = [
            {
                "team_number": "973",
                # Averages
                "avg_intakes": 16.0,
                "auto_avg_high_balls": 71.0,
                "auto_avg_low_balls": 60.0,
                "auto_avg_total_balls": 131.0,
                "tele_avg_high_balls": 38.0,
                "tele_avg_total_balls": 76.0,
                "tele_avg_low_balls": 38.0,
                "avg_incap_time": 18.0,
                # LFM Averages
                "lfm_auto_avg_high_balls": 71.0,
                "lfm_auto_avg_low_balls": 60.0,
                "lfm_tele_avg_high_balls": 38.0,
                "lfm_tele_avg_low_balls": 38.0,
                "lfm_avg_incap_time": 18.0,
                # Standard Deviations
                "auto_sd_high_balls": 14.854853303438128,
                "auto_sd_low_balls": 22.44994432064365,
                "tele_sd_high_balls": 27.796882319185844,
                "tele_sd_low_balls": 15.57776192739723,
                # Counts
                "matches_played": 3,
                "climb_all_attempts": 3,
                "low_rung_successes": 1,
                "mid_rung_successes": 0,
                "high_rung_successes": 1,
                "traversal_rung_successes": 0,
                "position_zero_starts": 0,
                "position_one_starts": 1,
                "position_two_starts": 1,
                "position_three_starts": 0,
                "position_four_starts": 1,
                "matches_incap": 3,
                # LFM Counts
                "lfm_climb_all_attempts": 3,
                "lfm_low_rung_successes": 1,
                "lfm_mid_rung_successes": 0,
                "lfm_high_rung_successes": 1,
                "lfm_traversal_rung_successes": 0,
                "lfm_matches_incap": 3,
                # Super Counts
                "matches_played_defense": 4,
                # Extrema
                "auto_max_low_balls": 84,
                "auto_max_high_balls": 92,
                "tele_max_low_balls": 56,
                "tele_max_high_balls": 68,
                "max_incap": 22,
                "max_climb_level": "HIGH",
                # LFM Extrema
                "lfm_auto_max_low_balls": 84,
                "lfm_auto_max_high_balls": 92,
                "lfm_tele_max_low_balls": 56,
                "lfm_tele_max_high_balls": 68,
                "lfm_max_incap": 22,
                "lfm_max_climb_level": "HIGH",
                # Modes
                "mode_climb_level": ["LOW", "NONE", "HIGH"],
                "mode_start_position": ["ONE", "TWO", "FOUR"],
                # LFM Modes
                "lfm_mode_start_position": ["ONE", "TWO", "FOUR"],
                # Success Rates
                "climb_percent_success": 0.6666666666666666,
                # LFM Success Rates
                "lfm_climb_percent_success": 0.6666666666666666,
                # Average Points
                "avg_climb_points": 7,
            },
            {
                "team_number": "1678",
                # Averages
                "auto_avg_high_balls": 37.0,
                "auto_avg_low_balls": 25.8,
                "auto_avg_total_balls": 62.8,
                "tele_avg_high_balls": 44.4,
                "tele_avg_low_balls": 42.2,
                "tele_avg_total_balls": 86.6,
                "avg_intakes": 20.6,
                "avg_incap_time": 27.4,
                # LFM Averages
                "lfm_auto_avg_high_balls": 27.25,
                "lfm_auto_avg_low_balls": 20.5,
                "lfm_tele_avg_high_balls": 35.25,
                "lfm_tele_avg_low_balls": 44.25,
                "lfm_avg_incap_time": 30.0,
                # Standard Deviations
                "auto_sd_high_balls": 29.5296461204668,
                "auto_sd_low_balls": 22.03088740836374,
                "tele_sd_high_balls": 33.332266649599454,
                "tele_sd_low_balls": 36.766288907095316,
                # Counts
                "matches_played": 5,
                "climb_all_attempts": 5,
                "low_rung_successes": 3,
                "mid_rung_successes": 1,
                "high_rung_successes": 0,
                "traversal_rung_successes": 1,
                "position_zero_starts": 0,
                "position_one_starts": 1,
                "position_two_starts": 0,
                "position_three_starts": 1,
                "position_four_starts": 3,
                "matches_incap": 5,
                # LFM Counts
                "lfm_climb_all_attempts": 4,
                "lfm_low_rung_successes": 3,
                "lfm_mid_rung_successes": 1,
                "lfm_high_rung_successes": 0,
                "lfm_traversal_rung_successes": 0,
                "lfm_matches_incap": 4,
                # Super Counts
                "matches_played_defense": 2,
                # Extrema
                "auto_max_low_balls": 54,
                "auto_max_high_balls": 76,
                "tele_max_low_balls": 89,
                "tele_max_high_balls": 81,
                "max_incap": 93,
                "max_climb_level": "TRAVERSAL",
                # LFM Extrema
                "lfm_auto_max_low_balls": 54,
                "lfm_auto_max_high_balls": 54,
                "lfm_tele_max_low_balls": 89,
                "lfm_tele_max_high_balls": 73,
                "lfm_max_incap": 93,
                "lfm_max_climb_level": "MID",
                # Modes
                "mode_climb_level": ["LOW"],
                "mode_start_position": ["FOUR"],
                # LFM Modes
                "lfm_mode_start_position": ["FOUR"],
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
