# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import obj_tims
from server import Server
import pytest


@pytest.mark.clouddb
class TestObjTIMCalcs:
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
                {"in_teleop": True, "time": 70, "action_type": "failed_score"},
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
                {"in_teleop": True, "time": 70, "action_type": "failed_score"},
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
                {"in_teleop": True, "time": 70, "action_type": "failed_score"},
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

    @mock.patch.object(base_calculations.BaseCalculations, "get_teams_list", return_value=["3"])
    def setup_method(self, method, get_teams_list_dummy):
        with mock.patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calculator = obj_tims.ObjTIMCalcs(self.test_server)

    def test_modes(self):
        assert self.test_calculator.modes([3, 3, 3]) == [3]
        assert self.test_calculator.modes([]) == []
        assert self.test_calculator.modes([1, 1, 2, 2]) == [1, 2]
        assert self.test_calculator.modes([1, 1, 2, 2, 3]) == [1, 2]
        assert self.test_calculator.modes([1, 2, 3, 1]) == [1]
        assert self.test_calculator.modes([1, 4, 3, 4]) == [4]
        assert self.test_calculator.modes([9, 6, 3, 9]) == [9]

    def test_consolidate_nums(self):
        assert self.test_calculator.consolidate_nums([3, 3, 3]) == 3
        assert self.test_calculator.consolidate_nums([4, 4, 4, 4, 1]) == 4
        assert self.test_calculator.consolidate_nums([2, 2, 1]) == 2
        assert self.test_calculator.consolidate_nums([]) == 0

    def test_consolidate_bools(self):
        assert self.test_calculator.consolidate_bools([True, True, True]) == True
        assert self.test_calculator.consolidate_bools([False, True, True]) == True
        assert self.test_calculator.consolidate_bools([False, False, True]) == False
        assert self.test_calculator.consolidate_bools([False, False, False]) == False

    def test_filter_timeline_actions(self):
        actions = self.test_calculator.filter_timeline_actions(self.unconsolidated_tims[0])
        assert actions == [
            {"in_teleop": True, "time": 2, "action_type": "end_incap"},
            {"in_teleop": True, "time": 35, "action_type": "start_incap"},
            {"in_teleop": True, "time": 51, "action_type": "score_cone_high"},
            {"in_teleop": True, "time": 68, "action_type": "score_cone_low"},
            {"in_teleop": True, "time": 70, "action_type": "failed_score"},
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
        assert action_num == 22

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert total_time(self.unconsolidated_tims[0], "start_incap", "end_incap", 8) == 33
        assert total_time(self.unconsolidated_tims[2], "start_incap", "end_incap", 8) == 43

    def test_run_consolidation(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        self.test_calculator.run()
        result = self.test_server.db.find("obj_tim")
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["incap"] == 33
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == "254"
        assert calculated_tim["auto_total_cones"] == 4
        assert calculated_tim["auto_total_cubes"] == 4
        assert calculated_tim["auto_total_gamepieces"] == 8
        assert calculated_tim["tele_total_cones"] == 5
        assert calculated_tim["tele_total_cubes"] == 4
        assert calculated_tim["tele_total_gamepieces"] == 9
        assert calculated_tim["auto_charge_level"] == "DOCK"
        assert calculated_tim["tele_charge_level"] == "PARK"
        assert calculated_tim["start_position"] == "1"
        assert calculated_tim["preloaded_gamepiece"] == "CUBE"
        assert calculated_tim["failed_scores"] == 1

    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        "entries_since_last",
        return_value=[{"o": {"team_number": "1", "match_number": 2}}],
    )
    def test_in_list_check1(self, entries_since_last_dummy):
        with mock.patch("utils.log_warning") as warning_check:
            self.test_calculator.run()
            warning_check.assert_called()

    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        "entries_since_last",
        return_value=[{"o": {"team_number": "3", "match_number": 2}}],
    )
    @mock.patch.object(obj_tims.ObjTIMCalcs, "update_calcs", return_value=[{}])
    def test_in_list_check2(self, entries_since_last_dummy, update_calcs_dummy):
        with mock.patch("utils.log_warning") as warning_check:
            self.test_calculator.run()
            warning_check.assert_not_called()
