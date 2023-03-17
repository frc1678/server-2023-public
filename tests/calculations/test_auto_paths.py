# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import obj_tims
from calculations import auto_paths
from server import Server
import pytest


class TestAutoPathCalc:
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
                {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
                {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ],
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
                {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
                {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ],
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
                {"in_teleop": False, "time": 137, "action_type": "start_incap"},
                {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
                {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ],
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
            {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
            {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
            {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
            {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ],
        [
            {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
            {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
            {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ],
        [
            {"in_teleop": False, "time": 137, "action_type": "start_incap"},
            {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
            {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
            {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
            {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
            {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
            {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
            {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
        ],
    ]
    expected_consolidated_timelines = [
        {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
        {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
        {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
        {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
        {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
        {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
        {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
        {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
    ]
    expected_auto_variables = {
        "start_position": "1",
        "preloaded_gamepiece": "U",
        "auto_charge_level": "D",
    }
    expected_auto_paths = [
        {
            "match_number": 42,
            "team_number": "254",
            "start_position": "1",
            "preloaded_gamepiece": "U",
            "auto_charge_level": "D",
            "auto_timeline": [
                {"in_teleop": False, "time": 138, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 139, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 140, "action_type": "score_cube_low"},
                {"in_teleop": False, "time": 143, "action_type": "score_cube_mid"},
                {"in_teleop": False, "time": 145, "action_type": "score_cube_high"},
                {"in_teleop": False, "time": 146, "action_type": "score_cone_low"},
                {"in_teleop": False, "time": 148, "action_type": "score_cone_mid"},
                {"in_teleop": False, "time": 150, "action_type": "score_cone_high"},
            ],
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

    def test___init__(self):
        assert self.test_calculator.server == self.test_server
        assert self.test_calculator.watched_collections == [
            "auto_paths",
            "unconsolidated_obj_tim",
            "obj_tim",
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
        # Insert test data for the run function
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_obj_tims)
        self.test_server.db.insert_documents("obj_tim", self.calculated_obj_tims)

        self.test_calculator.run()
        result = self.test_server.db.find("auto_paths")

        for document in result:
            del document["_id"]

        assert result == self.expected_auto_paths
