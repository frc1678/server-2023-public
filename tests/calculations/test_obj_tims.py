# Copyright (c) 2019 FRC Team 1678: Citrus Circuits

from src.calculations import obj_tims

UNCONSOLIDATED_QR_ONE = {
    "schema_version": 18,
    "serial_number": "STR6",
    "match_number": 428,
    "timestamp": 5,
    "match_collection_version_number": "STR5",
    "scout_name": "EDWIN",
    "team_number": 254,
    "scout_id": 17,
    "timeline": [
        {"time": 3, "action_type": "end_climb"},
        {"time": 15, "action_type": "score_ball_high"},
        {"time": 26, "action_type": "score_ball_low"},
        {"time": 37, "action_type": "score_ball_high"},
        {"time": 47, "action_type": "score_ball_high"},
        {"time": 53, "action_type": "start_climb"},
        {"time": 69, "action_type": "score_ball_high"},
        {"time": 80, "action_type": "score_ball_high"},
        {"time": 90, "action_type": "score_ball_high"},
        {"time": 103, "action_type": "score_ball_high"},
    ],
}

UNCONSOLIDATED_QR_TWO = {
    "schema_version": 18,
    "serial_number": "STR2",
    "match_number": 424,
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
}

UNCONSOLIDATED_QR_THREE = {
    "schema_version": 18,
    "serial_number": "STR5",
    "match_number": 421,
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
        {"time": 68, "action_type": "score_ball_high"},
        {"time": 79, "action_type": "start_climb"},
    ],
}


def test_modes():
    nums_lists = [
        {"list": [1, 2, 3, 1], "common": 1},
        {"list": [1, 4, 3, 4], "common": 4},
        {"list": [9, 6, 3, 9], "common": 9},
    ]

    for num_list in nums_lists:
        assert obj_tims.modes(num_list["list"])[0] == num_list["common"]


def test_consolidate_nums():
    # Test if all the values are the same
    assert obj_tims.consolidate_nums([3, 3, 3]) == 3

    # Test if the list is empty
    assert obj_tims.consolidate_nums([]) == 0

    # Test behavior for different lengths
    for value in range(10):
        for x in range(2, 10):
            test_list = [value] * x + [value + 1]
            assert obj_tims.consolidate_nums(test_list) == value


def test_consolidate_bools():
    bools_lists = [
        {"list": [True, True, False], "common": True},
        {"list": [False, True, True], "common": True},
        {"list": [False, False, True], "common": False},
        {"list": [False, False, False], "common": False},
    ]

    for bools_list in bools_lists:
        assert obj_tims.consolidate_bools(bools_list["list"]) == bools_list["common"]


def test_filter_timeline_actions():
    actions = obj_tims.filter_timeline_actions(UNCONSOLIDATED_QR_ONE)
    assert actions[0] == {'action_type': 'end_climb', 'time': 3}
    assert actions[1] == {'action_type': 'score_ball_high', 'time': 15}
    assert actions[2] == {'action_type': 'score_ball_low', 'time': 26}
    assert actions[3] == {'action_type': 'score_ball_high', 'time': 37}
    assert actions[4] == {'action_type': 'score_ball_high', 'time': 47}
    assert actions[5] == {'action_type': 'start_climb', 'time': 53}
    assert actions[6] == {'action_type': 'score_ball_high', 'time': 69}
    assert actions[7] == {'action_type': 'score_ball_high', 'time': 80}
    assert actions[8] == {'action_type': 'score_ball_high', 'time': 90}
    assert actions[9] == {'action_type': 'score_ball_high', 'time': 103}


def test_count_timeline_actions():
    action_num = obj_tims.count_timeline_actions(UNCONSOLIDATED_QR_ONE)
    assert action_num == 10


def test_total_time_between_actions():
    total_time = obj_tims.total_time_between_actions
    assert total_time(UNCONSOLIDATED_QR_ONE, "score_ball_high", "end_climb") == 12
    assert total_time(UNCONSOLIDATED_QR_ONE, "score_ball_low", "end_climb") == 23
    assert total_time(UNCONSOLIDATED_QR_ONE, "start_climb", "end_climb") == 50


def test_calculate_tim():
    cal_tim = obj_tims.calculate_tim(
        [UNCONSOLIDATED_QR_ONE, UNCONSOLIDATED_QR_TWO, UNCONSOLIDATED_QR_THREE]
    )
    assert cal_tim["auto_balls_high"] == 0
    assert cal_tim["auto_balls_low"] == 0
    assert cal_tim["climb_time"] == 50
    assert cal_tim["confidence_ranking"] == 3
    assert cal_tim["control_panel_position"] == False
    assert cal_tim["control_panel_rotation"] == False
    assert cal_tim["incap"] == 0
    assert cal_tim["match_number"] == 428
    assert cal_tim["team_number"] == 254
    assert cal_tim["tele_balls_high"] == 7
    assert cal_tim["tele_balls_low"] == 1

def test_update_calc_obj_tims():
    # TODO: We need to add tests to this after ldc is updated with new structure
    pass
