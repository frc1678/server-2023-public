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
            'schema_version': 2,
            'serial_number': 'STR6',
            'match_number': 42,
            'timestamp': 5,
            'match_collection_version_number': 'STR5',
            'scout_name': 'EDWIN',
            'team_number': 254,
            'scout_id': 17,
            'timeline': [
                {'time': 3, 'action_type': 'end_climb'},
                {'time': 15, 'action_type': 'score_ball_high_other'},
                {'time': 26, 'action_type': 'score_ball_low'},
                {'time': 37, 'action_type': 'end_incap'},
                {'time': 47, 'action_type': 'start_incap'},
                {'time': 53, 'action_type': 'start_climb'},
                {'time': 69, 'action_type': 'score_ball_high_other'},
                {'time': 80, 'action_type': 'score_ball_high_launchpad'},
                {'time': 90, 'action_type': 'score_ball_high_hub'},
                {'time': 96, 'action_type': 'score_ball_low'},
                {'time': 103, 'action_type': 'score_ball_high_hub'},
                {'time': 110, 'action_type': 'score_opponent_ball'},
                {'time': 111, 'action_type': 'score_opponent_ball'},
                {'time': 135, 'action_type': 'score_ball_low'},
                {'time': 140, 'action_type': 'score_ball_high_hub'},
            ],
            'climb_level': 'TRAVERSAL',
            'start_position': 'ONE'
        },
        {
            'schema_version': 2,
            'serial_number': 'STR2',
            'match_number': 42,
            'timestamp': 6,
            'match_collection_version_number': 'STR1',
            'scout_name': 'EDWIN',
            'team_number': 254,
            'scout_id': 17,
            'timeline': [
                {'time': 5, 'action_type': 'score_ball_high_launchpad'},
                {'time': 15, 'action_type': 'score_ball_high_other'},
                {'time': 26, 'action_type': 'score_ball_low'},
                {'time': 37, 'action_type': 'score_ball_high_hub'},
                {'time': 47, 'action_type': 'score_ball_high_hub'},
                {'time': 58, 'action_type': 'score_ball_high_other'},
                {'time': 68, 'action_type': 'score_ball_high_other'},
                {'time': 80, 'action_type': 'score_ball_high_launchpad'},
                {'time': 90, 'action_type': 'score_ball_high_hub'},
                {'time': 96, 'action_type': 'score_ball_low'},
                {'time': 101, 'action_type': 'score_ball_high_hub'},
                {'time': 110, 'action_type': 'score_opponent_ball'},
                {'time': 111, 'action_type': 'score_opponent_ball'},
                {'time': 112, 'action_type': 'score_ball_high_launchpad'},
                {'time': 122, 'action_type': 'score_ball_high_other'},
                {'time': 136, 'action_type': 'score_ball_low'},
                {'time': 140, 'action_type': 'score_ball_high_hub'},
            ],
            'climb_level': 'HIGH',
            'start_position': 'TWO'

        },
        {
            'schema_version': 2,
            'serial_number': 'STR5',
            'match_number': 42,
            'timestamp': 11,
            'match_collection_version_number': 'STR6',
            'scout_name': 'EDWIN',
            'team_number': 254,
            'scout_id': 17,
            'timeline': [
                {'time': 4, 'action_type': 'end_climb'},
                {'time': 26, 'action_type': 'score_ball_low'},
                {'time': 37, 'action_type': 'score_ball_high_hub'},
                {'time': 47, 'action_type': 'score_ball_high_launchpad'},
                {'time': 58, 'action_type': 'score_ball_high_hub'},
                {'time': 69, 'action_type': 'score_ball_high_far_other'},
                {'time': 79, 'action_type': 'start_climb'},
                {'time': 96, 'action_type': 'score_ball_low'},
            ],
            'climb_level': 'HIGH',
            'start_position': 'FOUR'

        },
    ]

    @mock.patch.object(base_calculations.BaseCalculations, '_get_teams_list', return_value=[3])
    def setup_method(self, method, get_teams_list_dummy):
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
            {'action_type': 'score_ball_high_other', 'time': 15},
            {'action_type': 'score_ball_low', 'time': 26},
            {'action_type': 'end_incap', 'time': 37},
            {'action_type': 'start_incap', 'time': 47},
            {'action_type': 'start_climb', 'time': 53},
            {'action_type': 'score_ball_high_other', 'time': 69},
            {'action_type': 'score_ball_high_launchpad', 'time': 80},
            {'action_type': 'score_ball_high_hub', 'time': 90},
            {'action_type': 'score_ball_low', 'time': 96},
            {'action_type': 'score_ball_high_hub', 'time': 103},
            {'action_type': 'score_opponent_ball', 'time': 110 },
            {'action_type': 'score_opponent_ball', 'time': 111 },
            {'action_type': 'score_ball_low', 'time': 135},
            {'action_type': 'score_ball_high_hub', 'time': 140},
        ]

    def test_count_timeline_actions(self):
        action_num = self.test_calculator.count_timeline_actions(self.unconsolidated_tims[0])
        assert action_num == 15

    def test_total_time_between_actions(self):
        total_time = self.test_calculator.total_time_between_actions
        assert total_time(self.unconsolidated_tims[0], 'start_climb', 'end_climb') == 50
        assert total_time(self.unconsolidated_tims[0], 'start_incap', 'end_incap') == 10

    def test_run_consolidation(self):
        self.test_server.db.insert_documents('unconsolidated_obj_tim', self.unconsolidated_tims)
        self.test_calculator.run()
        result = self.test_server.db.find('obj_tim')
        assert len(result) == 1
        calculated_tim = result[0]
        assert calculated_tim['climb_time'] == 50
        assert calculated_tim['confidence_ranking'] == 3
        assert calculated_tim['incap'] == 0
        assert calculated_tim['match_number'] == 42
        assert calculated_tim['team_number'] == 254
        assert calculated_tim['auto_hub_highs'] == 1
        assert calculated_tim['auto_launchpad_highs'] == 0
        assert calculated_tim['auto_other_highs'] == 0
        assert calculated_tim['auto_lows'] == 1
        assert calculated_tim['tele_hub_highs'] == 2
        assert calculated_tim['tele_launchpad_highs'] == 1
        assert calculated_tim['tele_other_highs'] == 2
        assert calculated_tim['tele_lows'] == 2
        assert calculated_tim['opp_balls_scored'] == 2
        assert calculated_tim['auto_balls_high'] == 1
        assert calculated_tim['tele_balls_high'] == 5
        assert calculated_tim['climb_level'] == 'HIGH'
        assert calculated_tim['start_position'] == 'TWO'
        assert calculated_tim['auto_balls_total'] == 2
        assert calculated_tim['tele_balls_total'] == 7


    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        'entries_since_last',
        return_value=[{'o': {'team_number': 1, 'match_number': 2}}],
    )
    def test_in_list_check1(self, entries_since_last_dummy):
        with mock.patch('utils.log_warning') as warning_check:
            self.test_calculator.run()
            warning_check.assert_called()

    @mock.patch.object(
        obj_tims.ObjTIMCalcs,
        'entries_since_last',
        return_value=[{'o': {'team_number': 3, 'match_number': 2}}],
    )
    @mock.patch.object(obj_tims.ObjTIMCalcs, 'update_obj_tim_calcs', return_value=[{}])
    def test_in_list_check2(self, entries_since_last_dummy, update_obj_tim_calcs_dummy):
        with mock.patch('utils.log_warning') as warning_check:
            self.test_calculator.run()
            warning_check.assert_not_called()
