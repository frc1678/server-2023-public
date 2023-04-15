# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import unconsolidated_totals
from server import Server
import pytest


@pytest.mark.clouddb
class TestUnconsolidatedTotals:
    unconsolidated_tims = [
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
                {"in_teleop": True, "time": 2, "action_type": "end_incap"},
                {"in_teleop": True, "time": 35, "action_type": "start_incap"},
                {"in_teleop": True, "time": 51, "action_type": "score_cone_high"},
                {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
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
            "preloaded_gamepiece": "B",
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
            "preloaded_gamepiece": "B",
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
            "preloaded_gamepiece": "N",
        },
    ]

    @mock.patch.object(
        base_calculations.BaseCalculations, "get_teams_list", return_value=["3", "254", "1"]
    )
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = unconsolidated_totals.UnconsolidatedTotals(self.test_server)

    def test_filter_timeline_actions(self):
        actions = self.test_calculator.filter_timeline_actions(self.unconsolidated_tims[0])
        assert actions == [
            {"in_teleop": True, "time": 2, "action_type": "end_incap"},
            {"in_teleop": True, "time": 35, "action_type": "start_incap"},
            {"in_teleop": True, "time": 51, "action_type": "score_cone_high"},
            {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
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
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 21

    def test_calculate_unconsolidated_tims(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        self.test_calculator.run()
        result = self.test_server.db.find("unconsolidated_totals")
        assert len(result) == 3
        calculated_tim = result[0]
        del calculated_tim["_id"]
        assert calculated_tim == {
            "match_number": 42,
            "scout_name": "EDWIN",
            "team_number": "254",
            "alliance_color_is_red": True,
            "auto_cube_low": 1,
            "auto_cube_mid": 2,
            "auto_cube_high": 1,
            "auto_total_cubes": 4,
            "auto_cone_low": 2,
            "auto_cone_mid": 1,
            "auto_cone_high": 1,
            "auto_total_cones": 4,
            "auto_total_gamepieces": 0,
            "auto_total_gamepieces_low": 3,
            "tele_cube_low": 1,
            "tele_cube_mid": 2,
            "tele_cube_high": 1,
            "tele_total_cubes": 4,
            "tele_cone_low": 2,
            "tele_cone_mid": 1,
            "tele_cone_high": 2,
            "tele_total_cones": 5,
            "tele_total_gamepieces": 0,
            "failed_scores": 0,
            "intakes_low_row": 0,
            "intakes_mid_row": 0,
            "intakes_high_row": 0,
            "intakes_single": 0,
            "intakes_double": 0,
            "intakes_ground": 0,
            "total_intakes": 0,
            "auto_charge_attempt": 0,
            "tele_charge_attempt": 0,
            "total_charge_attempts": 0,
            "tele_total_gamepieces_low": 3,
            "auto_charge_level": "D",
            "tele_charge_level": "P",
            "start_position": "1",
            "preloaded_gamepiece": "B",
        }

    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals,
        "entries_since_last",
        return_value=[{"o": {"team_number": "1", "match_number": 2}}],
    )
    def test_in_list_check1(self, entries_since_last_dummy, caplog):
        self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) > 0

    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals,
        "entries_since_last",
        return_value=[{"o": {"team_number": "3", "match_number": 2}}],
    )
    @mock.patch.object(
        unconsolidated_totals.UnconsolidatedTotals, "update_calcs", return_value=[{}]
    )
    def test_in_list_check2(self, entries_since_last_dummy, update_calcs_dummy, caplog):
        self.test_calculator.run()
        assert len([rec.message for rec in caplog.records if rec.levelname == "WARNING"]) == 0
