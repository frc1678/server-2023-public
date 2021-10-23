# Copyright (c) 2019 FRC Team 1678: Citrus Circuits

import pytest
from unittest import mock
from unittest.mock import PropertyMock

from server import Server
from calculations import tba_tims


TEST_DATA = [
    {
        'alliances': {
            'blue': {
                'team_keys': ['frc33', 'frc25', 'frc257'],
            },
            'red': {
                'team_keys': ['frc34', 'frc973', 'frc254'],
            },
        },
        'comp_level': 'qm',
        'match_number': 1,
        'score_breakdown': {
            'blue': {
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Park',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'NotLevel',
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
            },
            'red': {
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Park',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'NotLevel',
                'initLineRobot1': 'Hand',
                'initLineRobot2': 'Park',
                'initLineRobot3': 'None',
            },
        },
    },
    {
        'alliances': {
            'blue': {
                'team_keys': ['frc97', 'frc3', 'frc37'],
            },
            'red': {
                'team_keys': ['frc47', 'frc57', 'frc67'],
            },
        },
        'comp_level': 'qm',
        'match_number': 2,
        'score_breakdown': {
            'blue': {
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'Park',
                'endgameRungIsLevel': 'NotLevel',
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
            },
            'red': {
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'NotLevel',
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
            },
        },
    },
]

TIMS = [
    {
        "team_number": 254,
        "match_number": 1,
        "auto_line": False,
        "climb": False,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 973,
        "match_number": 1,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 34,
        "match_number": 1,
        "auto_line": False,
        "climb": False,
        "park": True,
        "level_climb": False,
    },
    {
        "team_number": 33,
        "match_number": 1,
        "auto_line": False,
        "climb": False,
        "park": True,
        "level_climb": False,
    },
    {
        "team_number": 25,
        "match_number": 1,
        "auto_line": False,
        "climb": False,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 257,
        "match_number": 1,
        "auto_line": False,
        "climb": False,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 97,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 3,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 37,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 47,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 57,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
    {
        "team_number": 67,
        "match_number": 2,
        "auto_line": True,
        "climb": True,
        "park": False,
        "level_climb": False,
    },
]


@pytest.fixture(autouse=True, scope="function")
def mock_entries_since_last():
    with mock.patch.object(tba_tims.TBATIMCalc, "entries_since_last", return_value=TEST_DATA) as _:
        yield


@pytest.mark.clouddb
class TestTBATimCalc:
    def setup_method(self):
        self.test_server = Server()
        self.test_calc = tba_tims.TBATIMCalc(self.test_server)

    def test_calc_tba_bool(self):
        # Creates example match data to test calc_tba_bool()
        match_data = {
            "score_breakdown": {
                "blue": {
                    "initLineRobot1": "Exited",
                    "initLineRobot2": "Exited",
                    "initLineRobot3": "Exited",
                    "endgameRobot1": "Hang",
                    "endgameRobot2": "Park",
                    "endgameRobot3": "None",
                    "endgameRungIsLevel": "IsLevel",
                },
                "red": {
                    "initLineRobot1": "Exited",
                    "initLineRobot2": "None",
                    "initLineRobot3": "Exited",
                    "endgameRobot1": "Hang",
                    "endgameRobot2": "Park",
                    "endgameRobot3": "None",
                    "endgameRungIsLevel": "IsNotLevel",
                },
            }
        }

        # Tests calc_tba_bool() using the example match data above
        assert tba_tims.TBATIMCalc.calc_tba_bool(match_data, "blue", {"initLineRobot1": "Exited"})
        assert not tba_tims.TBATIMCalc.calc_tba_bool(
            match_data, "red", {"initLineRobot2": "Exited"}
        )
        assert tba_tims.TBATIMCalc.calc_tba_bool(match_data, "red", {"endgameRobot2": "Park"})
        assert not tba_tims.TBATIMCalc.calc_tba_bool(match_data, "blue", {"endgameRobot3": "Hang"})
        assert not tba_tims.TBATIMCalc.calc_tba_bool(
            match_data, "red", {"endgameRobot1": "Hang", "endgameRungIsLevel": "IsLevel"}
        )
        assert not tba_tims.TBATIMCalc.calc_tba_bool(
            match_data, "blue", {"endgameRobot2": "Hang", "endgameRungIsLevel": "IsLevel"}
        )
        assert tba_tims.TBATIMCalc.calc_tba_bool(
            match_data, "blue", {"endgameRobot1": "Hang", "endgameRungIsLevel": "IsLevel"}
        )

    def test_get_robot_number_and_alliance(self):
        # Generates example team keys to test get_robot_number_and_alliance()
        match_data = {
            "alliances": {
                "blue": {"team_keys": ["frc1678", "frc254", "frc413"]},
                "red": {"team_keys": ["frc612", "frc1024", "frc687"]},
            },
            "match_number": 1,
        }

        # Uses example team keys above to test get_robot_number_and_alliance()
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(1678, match_data) == (1, "blue")
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(1024, match_data) == (2, "red")
        assert tba_tims.TBATIMCalc.get_robot_number_and_alliance(413, match_data) == (3, "blue")
        with pytest.raises(ValueError):
            tba_tims.TBATIMCalc.get_robot_number_and_alliance(977, match_data)

    def test_get_team_list_from_match(self):
        # Creates example match data for testing get_team_list_from_match()
        match_data = {
            "alliances": {
                "blue": {"team_keys": ["frc1678", "frc254", "frc413"]},
                "red": {"team_keys": ["frc612", "frc1024", "frc687"]},
            }
        }

        # Ensures the team data is reformatted correctly in get_team_list_from_match()
        assert sorted(tba_tims.TBATIMCalc.get_team_list_from_match(match_data)) == sorted(
            [612, 1024, 687, 1678, 254, 413]
        )

    def test_calculate_tim(self):
        for match in TEST_DATA:
            for team_number in self.test_calc.get_team_list_from_match(match):
                calc = self.test_calc.calculate_tim(team_number, match)
                assert isinstance(calc, dict)
                assert isinstance(calc["team_number"], int)
                assert isinstance(calc["match_number"], int)
                assert isinstance(calc["auto_line"], bool)
                assert isinstance(calc["climb"], bool)
                assert isinstance(calc["park"], bool)
                assert isinstance(calc["level_climb"], bool)

    def test_run(self):
        entries = self.test_calc.entries_since_last()
        for entry in entries:
            for _ in self.test_calc.get_team_list_from_match(entry):
                assert entry["match_number"] not in self.test_calc.calculated

        self.test_calc.run()
        for entry in entries:
            for _ in self.test_calc.get_team_list_from_match(entry):
                assert entry["match_number"] in self.test_calc.calculated
