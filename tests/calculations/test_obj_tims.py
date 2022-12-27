# Copyright (c) 2022 FRC Team 1678: Citrus Circuits

from unittest import mock

from calculations import base_calculations
from calculations import obj_tims
from server import Server
import pytest


@pytest.mark.clouddb
class TestObjTIMCalcs:
    unconsolidated_tims = [
        {
            "schema_version": 2,
            "serial_number": "STR6",
            "match_number": 42,
            "timestamp": 5,
            "match_collection_version_number": "STR5",
            "scout_name": "EDWIN",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"time": 15, "action_type": "score_ball_high"},
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "end_incap"},
                {"time": 47, "action_type": "start_incap"},
                {"time": 69, "action_type": "score_ball_high"},
                {"time": 80, "action_type": "score_ball_high"},
                {"time": 90, "action_type": "score_ball_high"},
                {"time": 96, "action_type": "score_ball_low"},
                {"time": 103, "action_type": "score_ball_high"},
                {"time": 135, "action_type": "score_ball_low"},
                {"time": 140, "action_type": "score_ball_high"},
            ],
            "climb_level": "NONE",
            "start_position": "ONE",
        },
        {
            "schema_version": 2,
            "serial_number": "STR2",
            "match_number": 42,
            "timestamp": 6,
            "match_collection_version_number": "STR1",
            "scout_name": "RAY",
            "alliance_color_is_red": True,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"time": 5, "action_type": "score_ball_high"},
                {"time": 15, "action_type": "score_ball_high"},
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "score_ball_high"},
                {"time": 47, "action_type": "score_ball_high"},
                {"time": 58, "action_type": "score_ball_high"},
                {"time": 68, "action_type": "score_ball_high"},
                {"time": 80, "action_type": "score_ball_high"},
                {"time": 83, "action_type": "end_incap"},
                {"time": 90, "action_type": "score_ball_high"},
                {"time": 93, "action_type": "start_incap"},
                {"time": 96, "action_type": "score_ball_low"},
                {"time": 97, "action_type": "end_incap"},
                {"time": 101, "action_type": "score_ball_high"},
                {"time": 105, "action_type": "start_incap"},
                {"time": 112, "action_type": "score_ball_high"},
                {"time": 122, "action_type": "score_ball_high"},
                {"time": 133, "action_type": "end_incap"},
                {"time": 136, "action_type": "score_ball_low"},
                {"time": 138, "action_type": "start_incap"},
                {"time": 140, "action_type": "score_ball_high"},
            ],
            "climb_level": "HIGH",
            "start_position": "TWO",
        },
        {
            "schema_version": 2,
            "serial_number": "STR5",
            "match_number": 42,
            "timestamp": 11,
            "match_collection_version_number": "STR6",
            "scout_name": "ADRIAN",
            "alliance_color_is_red": False,
            "team_number": "254",
            "scout_id": 17,
            "timeline": [
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "score_ball_high"},
                {"time": 47, "action_type": "score_ball_high"},
                {"time": 58, "action_type": "score_ball_high"},
                {"time": 69, "action_type": "score_ball_high"},
                {"time": 79, "action_type": "start_climb"},
                {"time": 96, "action_type": "score_ball_low"},
            ],
            "climb_level": "HIGH",
            "start_position": "FOUR",
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
            {"action_type": "score_ball_high", "time": 15},
            {"action_type": "score_ball_low", "time": 26},
            {"action_type": "end_incap", "time": 37},
            {"action_type": "start_incap", "time": 47},
            {"action_type": "score_ball_high", "time": 69},
            {"action_type": "score_ball_high", "time": 80},
            {"action_type": "score_ball_high", "time": 90},
            {"action_type": "score_ball_low", "time": 96},
            {"action_type": "score_ball_high", "time": 103},
            {"action_type": "score_ball_low", "time": 135},
            {"action_type": "score_ball_high", "time": 140},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 11

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert total_time(self.unconsolidated_tims[0], "start_incap", "end_incap", 8) == 10
        assert total_time(self.unconsolidated_tims[1], "start_incap", "end_incap", 8) == 18

    def test_run_consolidation(self):
        self.test_server.db.insert_documents("unconsolidated_obj_tim", self.unconsolidated_tims)
        self.test_calculator.run()
        result = self.test_server.db.find("obj_tim")
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["incap"] == 10
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == "254"
        assert calculated_tim["auto_high_balls"] == 1
        assert calculated_tim["auto_low_balls"] == 1
        assert calculated_tim["tele_high_balls"] == 5
        assert calculated_tim["tele_low_balls"] == 2
        assert calculated_tim["auto_high_balls"] == 1
        assert calculated_tim["tele_high_balls"] == 5
        assert calculated_tim["climb_level"] == "HIGH"
        assert calculated_tim["start_position"] == "TWO"
        assert calculated_tim["auto_total_balls"] == 2
        assert calculated_tim["tele_total_balls"] == 7
        assert calculated_tim["climb_attempts"] == 1

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
