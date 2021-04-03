# Copyright (c) 2019 FRC Team 1678: Citrus Circuits

from calculations import obj_tims
from server import Server
import pytest


@pytest.mark.clouddb
class TestObjTIMCalcs:
    unconsolidated_tims = [
        {
            "schema_version": 18,
            "serial_number": "STR6",
            "match_number": 42,
            "timestamp": 5,
            "match_collection_version_number": "STR5",
            "scout_name": "EDWIN",
            "team_number": 254,
            "scout_id": 17,
            "timeline": [
                {"time": 3, "action_type": "end_climb"},
                {"time": 15, "action_type": "score_ball_high"},
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "end_incap"},
                {"time": 47, "action_type": "start_incap"},
                {"time": 53, "action_type": "start_climb"},
                {"time": 69, "action_type": "score_ball_high"},
                {"time": 80, "action_type": "score_ball_high"},
                {"time": 90, "action_type": "score_ball_high"},
                {"time": 103, "action_type": "score_ball_high"},
            ],
        },
        {
            "schema_version": 18,
            "serial_number": "STR2",
            "match_number": 42,
            "timestamp": 6,
            "match_collection_version_number": "STR1",
            "scout_name": "EDWIN",
            "team_number": 254,
            "scout_id": 17,
            "timeline": [
                {"time": 5, "action_type": "score_ball_high"},
                {"time": 15, "action_type": "score_ball_high"},
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "score_ball_high"},
                {"time": 47, "action_type": "score_ball_high"},
                {"time": 52, "action_type": "control_panel_rotation"},
                {"time": 58, "action_type": "score_ball_high"},
                {"time": 68, "action_type": "score_ball_high"},
                {"time": 80, "action_type": "score_ball_high"},
                {"time": 90, "action_type": "score_ball_high"},
                {"time": 101, "action_type": "score_ball_high"},
                {"time": 112, "action_type": "score_ball_high"},
                {"time": 122, "action_type": "score_ball_high"},
                {"time": 133, "action_type": "score_ball_low"},
                {"time": 144, "action_type": "score_ball_low"},
            ],
        },
        {
            "schema_version": 18,
            "serial_number": "STR5",
            "match_number": 42,
            "timestamp": 11,
            "match_collection_version_number": "STR6",
            "scout_name": "EDWIN",
            "team_number": 254,
            "scout_id": 17,
            "timeline": [
                {"time": 4, "action_type": "end_climb"},
                {"time": 26, "action_type": "score_ball_low"},
                {"time": 37, "action_type": "score_ball_high"},
                {"time": 47, "action_type": "score_ball_high"},
                {"time": 58, "action_type": "score_ball_high"},
                {"time": 64, "action_type": "control_panel_rotation"},
                {"time": 69, "action_type": "score_ball_high"},
                {"time": 79, "action_type": "start_climb"},
            ],
        },
    ]

    def setup_method(self, method):
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
            {'action_type': 'end_climb', 'time': 3},
            {'action_type': 'score_ball_high', 'time': 15},
            {'action_type': 'score_ball_low', 'time': 26},
            {'action_type': 'end_incap', 'time': 37},
            {'action_type': 'start_incap', 'time': 47},
            {'action_type': 'start_climb', 'time': 53},
            {'action_type': 'score_ball_high', 'time': 69},
            {'action_type': 'score_ball_high', 'time': 80},
            {'action_type': 'score_ball_high', 'time': 90},
            {'action_type': 'score_ball_high', 'time': 103},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 10

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert total_time(self.unconsolidated_tims[0], "start_climb", "end_climb") == 50
        assert total_time(self.unconsolidated_tims[0], "start_incap", "end_incap") == 10

    def test_run_consolidation(self):
        self.test_server.db.insert_documents('unconsolidated_obj_tim', self.unconsolidated_tims)
        self.test_calculator.run()
        result = self.test_server.db.find('obj_tim')
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim["auto_balls_high"] == 0
        assert calculated_tim["auto_balls_low"] == 0
        assert calculated_tim["climb_time"] == 50
        assert calculated_tim["confidence_ranking"] == 3
        assert calculated_tim["control_panel_position"] == False
        assert calculated_tim["control_panel_rotation"] == True
        assert calculated_tim["incap"] == 0
        assert calculated_tim["match_number"] == 42
        assert calculated_tim["team_number"] == 254
        assert calculated_tim["tele_balls_high"] == 5
        assert calculated_tim["tele_balls_low"] == 1
