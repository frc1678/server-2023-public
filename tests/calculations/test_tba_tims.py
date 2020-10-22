# Copyright (c) 2019 FRC Team 1678: Citrus Circuits

import pytest
from src.calculations import tba_tims


def test_calc_tba_bool():
    # Creates example match data to test calc_tba_bool()
    match_data = {"score_breakdown": {
        "blue": {
            "initLineRobot1": "Exited",
            "initLineRobot2": "Exited",
            "initLineRobot3": "Exited",
            "endgameRobot1": "Hang",
            "endgameRobot2": "Park",
            "endgameRobot3": "None",
            "endgameRungIsLevel": "IsLevel"},
        "red": {
            "initLineRobot1": "Exited",
            "initLineRobot2": "None",
            "initLineRobot3": "Exited",
            "endgameRobot1": "Hang",
            "endgameRobot2": "Park",
            "endgameRobot3": "None",
            "endgameRungIsLevel": "IsNotLevel"},
    }}

    # Tests calc_tba_bool() using the example match data above
    assert tba_tims.calc_tba_bool(match_data, "blue", {"initLineRobot1": "Exited"})
    assert not tba_tims.calc_tba_bool(match_data, "red", {"initLineRobot2": "Exited"})
    assert tba_tims.calc_tba_bool(match_data, "red", {"endgameRobot2": "Park"})
    assert not tba_tims.calc_tba_bool(match_data, "blue", {"endgameRobot3": "Hang"})
    assert not tba_tims.calc_tba_bool(match_data, "red", {"endgameRobot1": "Hang", "endgameRungIsLevel": "IsLevel"})
    assert not tba_tims.calc_tba_bool(match_data, "blue", {"endgameRobot2": "Hang", "endgameRungIsLevel": "IsLevel"})
    assert tba_tims.calc_tba_bool(match_data, "blue", {"endgameRobot1": "Hang", "endgameRungIsLevel": "IsLevel"})


def test_get_robot_number_and_alliance():
    # Generates example team keys to test get_robot_number_and_alliance()
    match_data = {"alliances": {
        "blue": {
            "team_keys": ["frc1678", "frc254", "frc413"]},
        "red": {
            "team_keys": ["frc612", "frc1024", "frc687"]},
    },
        "match_number": 1}

    # Uses example team keys above to test get_robot_number_and_alliance()
    assert tba_tims.get_robot_number_and_alliance(1678, match_data) == (1, "blue")
    assert tba_tims.get_robot_number_and_alliance(1024, match_data) == (2, "red")
    assert tba_tims.get_robot_number_and_alliance(413, match_data) == (3, "blue")
    with pytest.raises(ValueError):
        tba_tims.get_robot_number_and_alliance(977, match_data)


def test_get_team_list_from_match():
    # Creates example match data for testing get_team_list_from_match()
    match_data = {"alliances": {
        "blue": {
            "team_keys": ["frc1678", "frc254", "frc413"]},
        "red": {
            "team_keys": ["frc612", "frc1024", "frc687"]},
    }}

    # Ensures the team data is reformatted correctly in get_team_list_from_match()
    assert sorted(tba_tims.get_team_list_from_match(match_data)) == sorted([612, 1024, 687, 1678, 254, 413])
