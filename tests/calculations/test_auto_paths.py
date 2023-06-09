# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import obj_tims
from calculations import auto_paths
from server import Server
import pytest


class TestAutoPathCalc:

    obj_teams = [{"team_number": "254"}, {"team_number": "4414"}, {"team_number": "1678"}]

    tba_tims = [
        {
            "match_number": 42,
            "team_number": "254",
            "mobility": True,
        },
        {
            "match_number": 44,
            "team_number": "4414",
            "mobility": True,
        },
        {
            "match_number": 49,
            "team_number": "4414",
            "mobility": False,
        },
        {
            "match_number": 1,
            "team_number": "1678",
            "mobility": True,
        },
        {
            "match_number": 2,
            "team_number": "1678",
            "mobility": False,
        },
    ]
    unconsolidated_obj_tims = [
        {
            "schema_version": 6,
            "serial_number": "STR6",
            "match_number": 42,
            "timestamp": 5,
            "match_collection_version_number": "STR5",
            "scout_name": "EDWIN",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": True, "time": 3, "action_type": "end_incap"},
                {"in_teleop": True, "time": 35, "action_type": "start_incap"},
                {"in_teleop": True, "time": 51, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 71, "action_type": "failed_score"},
                {"in_teleop": True, "time": 75, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 81, "action_type": "score_cube_low"},
                {"in_teleop": True, "time": 94, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 105, "action_type": "score_cube_high"},
                {"in_teleop": True, "time": 110, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 117, "action_type": "score_cone_mid"},
                {"in_teleop": True, "time": 125, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ][::-1],
            "auto_charge_level": "D",
            "tele_charge_level": "P",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "override": {"failed_scores": 0},
        },
        {
            "schema_version": 6,
            "serial_number": "STR2",
            "match_number": 42,
            "timestamp": 6,
            "match_collection_version_number": "STR1",
            "scout_name": "RAY",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 12, "action_type": "start_incap"},
                {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 70, "action_type": "failed_score"},
                {"in_teleop": True, "time": 75, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 81, "action_type": "score_cube_low"},
                {"in_teleop": True, "time": 94, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 105, "action_type": "score_cube_high"},
                {"in_teleop": True, "time": 110, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 119, "action_type": "score_cone_mid"},
                {"in_teleop": True, "time": 125, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 130, "action_type": "end_incap"},
                {"in_teleop": True, "time": 132, "action_type": "start_incap"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ][::-1],
            "auto_charge_level": "E",
            "tele_charge_level": "N",
            "start_position": "3",
            "preloaded_gamepiece": "O",
            "override": {"failed_scores": 0},
        },
        {
            "schema_version": 6,
            "serial_number": "STR5",
            "match_number": 42,
            "timestamp": 11,
            "match_collection_version_number": "STR6",
            "scout_name": "ADRIAN",
            "alliance_color_is_red": False,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 35, "action_type": "start_incap"},
                {"in_teleop": True, "time": 45, "action_type": "score_cube_low"},
                {"in_teleop": True, "time": 51, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 73, "action_type": "failed_score"},
                {"in_teleop": True, "time": 75, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 81, "action_type": "score_cube_low"},
                {"in_teleop": True, "time": 94, "action_type": "score_cube_mid"},
                {"in_teleop": True, "time": 105, "action_type": "score_cube_high"},
                {"in_teleop": True, "time": 110, "action_type": "score_cone_low"},
                {"in_teleop": True, "time": 117, "action_type": "score_cone_mid"},
                {"in_teleop": True, "time": 127, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 127, "action_type": "end_incap"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ][::-1],
            "auto_charge_level": "N",
            "tele_charge_level": "D",
            "start_position": "1",
            "preloaded_gamepiece": "O",
            "override": {"failed_scores": 0},
        },
    ]
    calculated_obj_tims = [
        {
            "match_number": 42,
            "team_number": "254",
            "auto_charge_attempt": 0,
            "auto_charge_level": "D",
            "auto_cone_high": 1,
            "auto_cone_low": 2,
            "auto_cone_mid": 1,
            "auto_cube_high": 1,
            "auto_cube_low": 1,
            "auto_cube_mid": 2,
            "auto_total_cones": 4,
            "auto_total_cubes": 4,
            "auto_total_gamepieces": 8,
            "auto_total_gamepieces_low": 3,
            "confidence_ranking": 3,
            "failed_scores": 0,
            "incap": 33,
            "intakes_ground": 0,
            "intakes_high_row": 0,
            "intakes_low_row": 0,
            "intakes_mid_row": 0,
            "intakes_station": 0,
            "median_cycle_time": 5,
            "preloaded_gamepiece": "U",
            "start_position": "1",
            "tele_charge_attempt": 0,
            "tele_charge_level": "P",
            "tele_cone_high": 2,
            "tele_cone_low": 2,
            "tele_cone_mid": 1,
            "tele_cube_high": 1,
            "tele_cube_low": 1,
            "tele_cube_mid": 2,
            "tele_total_cones": 5,
            "tele_total_cubes": 4,
            "tele_total_gamepieces": 9,
            "tele_total_gamepieces_low": 3,
            "total_charge_attempts": 0,
            "total_intakes": 0,
        },
        {
            "match_number": 44,
            "team_number": "4414",
            "auto_charge_attempt": 0,
            "auto_charge_level": "D",
            "auto_cone_high": 2,
            "auto_cone_low": 1,
            "auto_cone_mid": 1,
            "auto_cube_high": 2,
            "auto_cube_low": 0,
            "auto_cube_mid": 2,
            "auto_total_cones": 5,
            "auto_total_cubes": 3,
            "auto_total_gamepieces": 8,
            "auto_total_gamepieces_low": 3,
            "confidence_ranking": 3,
            "failed_scores": 0,
            "incap": 16,
            "intakes_ground": 1,
            "intakes_high_row": 0,
            "intakes_low_row": 0,
            "intakes_mid_row": 0,
            "intakes_station": 10,
            "median_cycle_time": 4,
            "preloaded_gamepiece": "U",
            "start_position": "1",
            "tele_charge_attempt": 0,
            "tele_charge_level": "P",
            "tele_cone_high": 2,
            "tele_cone_low": 2,
            "tele_cone_mid": 2,
            "tele_cube_high": 1,
            "tele_cube_low": 1,
            "tele_cube_mid": 2,
            "tele_total_cones": 6,
            "tele_total_cubes": 4,
            "tele_total_gamepieces": 10,
            "tele_total_gamepieces_low": 3,
            "total_charge_attempts": 0,
            "total_intakes": 10,
        },
    ]
    expected_unconsolidated_auto_timelines = [
        [
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ][::-1],
        [
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ][::-1],
        [
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ][::-1],
    ]
    expected_consolidated_timelines = [
        {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
        {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
        {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
        {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
        {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
    ][::-1]
    expected_auto_variables = {
        "start_position": "1",
        "preloaded_gamepiece": "U",
        "auto_charge_level": "D",
        "match_numbers": [42],
    }
    subj_tims = [
        {
            "match_number": 42,
            "team_number": "254",
            "quickness_score": 3,
            "field_awareness_score": 3,
            "alliance_color_is_red": True,
            "auto_pieces_start_position": [1, 1, 1, 1],
        },
        {
            "match_number": 49,
            "team_number": "4414",
            "quickness_score": 3,
            "field_awareness_score": 3,
            "alliance_color_is_red": True,
            "auto_pieces_start_position": [1, 1, 1, 1],
        },
    ]
    auto_paths = [
        {
            "match_number": 24,
            "match_numbers": [24],
            "team_number": "1678",
            "start_position": "3",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "E",
            "score_1_piece": "cube",
            "score_1_position": "low",
            "score_2_piece": "cone",
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": "cube",
            "intake_2_position": "two",
            "score_3_piece": "cube",
            "score_3_position": "high",
            "mobility": True,
        },
        {
            "match_number": 42,
            "match_numbers": [42],
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_1_piece": "cone",
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": "cube",
            "intake_2_position": "two",
            "score_3_piece": "cube",
            "score_3_position": "low",
            "mobility": True,
        },
        {
            "match_number": 24,
            "match_numbers": [24],
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "score_1_piece": "cone",
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": None,
            "score_3_position": None,
            "mobility": True,
        },
        {
            "match_number": 23,
            "match_numbers": [23],
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_1_piece": "cone",
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": "cube",
            "intake_2_position": "one",
            "score_3_piece": "cube",
            "score_3_position": "high",
            "mobility": True,
        },
        {
            "match_number": 56,
            "match_numbers": [56],
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "score_1_piece": "cone",
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": "cube",
            "intake_2_position": "one",
            "score_3_piece": "fail",
            "score_3_position": "fail",
            "mobility": True,
        },
        {
            "match_number": 70,
            "match_numbers": [70],
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "F",
            "score_1_piece": "cone",
            "score_1_position": "mid",
            "score_2_piece": "fail",
            "score_2_position": "fail",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": None,
            "intake_2_position": "one",
            "score_3_piece": "fail",
            "score_3_position": "fail",
            "mobility": True,
        },
    ]
    expected_group_auto_paths = [
        {
            "path_number": 1,
            "match_number": 24,
            "match_numbers": [24],
            "matches_ran": 1,
            "team_number": "1678",
            "start_position": "3",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "E",
            "auto_charge_successes": 1,
            "score_1_piece": "cube",
            "score_1_piece_successes": 1,
            "score_1_max_piece_successes": 1,
            "score_1_position": "low",
            "score_2_piece": "cone",
            "score_2_piece_successes": 1,
            "score_2_max_piece_successes": 1,
            "score_2_position": "mid",
            "score_3_piece": "cube",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "high",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": "cube",
            "intake_2_position": "two",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_number": 42,
            "match_numbers": [42],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "auto_charge_successes": 0,
            "score_1_piece": "cone",
            "score_1_piece_successes": 1,
            "score_1_max_piece_successes": 1,
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_piece_successes": 1,
            "score_2_max_piece_successes": 1,
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": "cube",
            "intake_2_position": "two",
            "score_3_piece": "cube",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "low",
            "mobility": True,
        },
        {
            "path_number": 2,
            "match_number": 24,
            "match_numbers": [24],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "auto_charge_successes": 0,
            "score_1_piece": "cone",
            "score_1_piece_successes": 1,
            "score_1_max_piece_successes": 1,
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_piece_successes": 1,
            "score_2_max_piece_successes": 1,
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": None,
            "score_3_piece_successes": 0,
            "score_3_max_piece_successes": 0,
            "score_3_position": None,
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_number": 23,
            "match_numbers": [23],
            "matches_ran": 1,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "auto_charge_successes": 1,
            "score_1_piece": "cone",
            "score_1_piece_successes": 1,
            "score_1_max_piece_successes": 1,
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_piece_successes": 1,
            "score_2_max_piece_successes": 1,
            "score_2_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": "cube",
            "intake_2_position": "one",
            "score_3_piece": "cube",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "high",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_number": 56,
            "match_numbers": [56, 23],
            "matches_ran": 2,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "auto_charge_successes": 2,
            "score_1_piece": "cone",
            "score_1_piece_successes": 2,
            "score_1_max_piece_successes": 2,
            "score_1_position": "low",
            "score_2_piece": "cube",
            "score_2_piece_successes": 2,
            "score_2_max_piece_successes": 2,
            "score_2_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": "cube",
            "intake_2_position": "one",
            "score_3_piece": "cube",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "high",
            "mobility": True,
        },
        {
            "path_number": 1,
            "match_number": 70,
            "match_numbers": [70, 56, 23],
            "matches_ran": 3,
            "team_number": "1678",
            "start_position": "2",
            "preloaded_gamepiece": "O",
            "auto_charge_level": "E",
            "auto_charge_successes": 2,
            "score_1_piece": "cone",
            "score_1_piece_successes": 3,
            "score_1_max_piece_successes": 1,
            "score_1_position": "mid",
            "score_2_piece": "cube",
            "score_2_piece_successes": 2,
            "score_2_max_piece_successes": 2,
            "score_2_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "two",
            "intake_2_piece": "cube",
            "intake_2_position": "one",
            "score_3_piece": "cube",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "high",
            "mobility": True,
        },
    ]
    expected_auto_paths = [
        {
            "path_number": 1,
            "match_numbers": [42],
            "matches_ran": 1,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "auto_charge_successes": 0,
            "auto_timeline": [
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 147, "action_type": "auto_intake_two"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 149, "action_type": "auto_intake_one"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ][::-1],
            "score_1_piece": "cone",
            "score_1_piece_successes": 1,
            "score_1_max_piece_successes": 1,
            "score_1_position": "high",
            "score_2_piece": "cone",
            "score_2_piece_successes": 1,
            "score_2_max_piece_successes": 1,
            "score_2_position": "mid",
            "intake_1_piece": "cube",
            "intake_1_position": "one",
            "intake_2_piece": "cube",
            "intake_2_position": "two",
            "score_3_piece": "cone",
            "score_3_piece_successes": 1,
            "score_3_max_piece_successes": 1,
            "score_3_position": "low",
            "mobility": True,
        },
    ]

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["3", "254"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = auto_paths.AutoPathCalc(self.test_server)
        # Insert test data into database for testing
        self.test_server.db.insert_documents("obj_tim", self.calculated_obj_tims)
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_obj_tims)
        self.test_server.db.insert_documents("subj_tim", self.subj_tims)
        self.test_server.db.insert_documents("tba_tim", self.tba_tims)
        self.test_server.db.insert_documents("obj_team", self.obj_teams)

    def test___init__(self):
        assert self.test_calculator.server == self.test_server
        assert self.test_calculator.watched_collections == [
            "unconsolidated_obj_tim",
        ]

    def test_get_unconsolidated_auto_timelines(self):
        unconsolidated_auto_timelines = self.test_calculator.get_unconsolidated_auto_timelines(
            self.unconsolidated_obj_tims
        )
        assert unconsolidated_auto_timelines == self.expected_unconsolidated_auto_timelines

    def test_consolidate_timelines(self):
        consolidated_timeline = self.test_calculator.consolidate_timelines(
            self.expected_unconsolidated_auto_timelines
        )
        assert consolidated_timeline == self.expected_consolidated_timelines

    def test_get_consolidated_auto_variables(self):
        auto_variables = self.test_calculator.get_consolidated_auto_variables(
            self.calculated_obj_tims[0]
        )
        assert auto_variables == self.expected_auto_variables

    def test_create_auto_fields(self):
        assert self.test_calculator.create_auto_fields(
            {
                "match_number": 1,
                "match_numbers": [1],
                "team_number": "1678",
                "auto_timeline": [
                    {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                    {"in_teleop": False, "time": 139, "action_type": "auto_intake_four"},
                    {"in_teleop": False, "time": 140, "action_type": "score_cube_mid"},
                ],
            },
            {
                "match_number": 1,
                "team_number": "1678",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [1, 1, 0, 1],
            },
        ) == {
            "score_1_piece": "cone",
            "score_1_position": "low",
            "intake_1_piece": "cube",
            "intake_1_position": "four",
            "score_2_piece": "cube",
            "score_2_position": "mid",
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": None,
            "score_3_position": None,
            "mobility": True,
        }

        assert self.test_calculator.create_auto_fields(
            {
                "match_number": 2,
                "match_numbers": [2],
                "team_number": "1678",
                "auto_timeline": [
                    {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                    {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
                    {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                    {"in_teleop": False, "time": 139, "action_type": "score_cube_high"},
                ],
            },
            {
                "match_number": 2,
                "team_number": "1678",
                "quickness_score": 3,
                "field_awareness_score": 3,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [1, 1, 1, 1],
            },
        ) == {
            "score_1_piece": "cone",
            "score_1_position": "low",
            "intake_1_piece": None,
            "intake_1_position": None,
            "score_2_piece": "cube",
            "score_2_position": "mid",
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": "cone",
            "score_3_position": "low",
            "score_4_piece": "cube",
            "score_4_position": "high",
            "mobility": False,
        }

        assert self.test_calculator.create_auto_fields(
            {"team_number": "4414", "match_number": 49, "match_numbers": [49], "auto_timeline": []},
            {},
        ) == {
            "score_1_piece": None,
            "score_1_position": None,
            "score_2_piece": None,
            "score_2_position": None,
            "intake_1_piece": None,
            "intake_1_position": None,
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": None,
            "score_3_position": None,
            "mobility": False,
        }

    def test_group_auto_paths(self):
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[0], [])
            == self.expected_group_auto_paths[0]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[0])
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[1], [])
            == self.expected_group_auto_paths[1]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[1])
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[2], [])
            == self.expected_group_auto_paths[2]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[2])
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[3], [])
            == self.expected_group_auto_paths[3]
        )
        self.test_server.db.insert_documents("auto_paths", self.expected_group_auto_paths[3])
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[4], [])
            == self.expected_group_auto_paths[4]
        )
        self.test_server.db.update_document(
            "auto_paths",
            self.expected_group_auto_paths[4],
            {
                "team_number": self.expected_group_auto_paths[4]["team_number"],
                "start_position": self.expected_group_auto_paths[4]["start_position"],
                "path_number": self.expected_group_auto_paths[4]["path_number"],
            },
        )
        assert (
            self.test_calculator.group_auto_paths(self.auto_paths[5], [])
            == self.expected_group_auto_paths[5]
        )
        self.test_server.db.update_document(
            "auto_paths",
            self.expected_group_auto_paths[5],
            {
                "team_number": self.expected_group_auto_paths[5]["team_number"],
                "start_position": self.expected_group_auto_paths[5]["start_position"],
                "path_number": self.expected_group_auto_paths[5]["path_number"],
            },
        )

    def test_calculate_auto_paths(self):
        calculated_auto_paths = self.test_calculator.calculate_auto_paths(
            [{"match_number": 42, "team_number": "254"}]
        )
        assert calculated_auto_paths == self.expected_auto_paths

    def test_run(self):
        # Delete any data that is already in the database collections
        self.test_server.db.delete_data("auto_paths")
        self.test_server.db.delete_data("unconsolidated_obj_tim")
        self.test_server.db.delete_data("obj_tim")
        self.test_server.db.delete_data("subj_tim")
        # Insert test data for the run function
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_obj_tims)
        self.test_server.db.insert_documents("obj_tim", self.calculated_obj_tims)
        self.test_server.db.insert_documents("subj_tim", self.subj_tims)

        self.test_calculator.run()
        result = self.test_server.db.find("auto_paths")

        for document in result:
            del document["_id"]

        assert result == self.expected_auto_paths
