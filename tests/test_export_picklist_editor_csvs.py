from data_transfer import database
import utils
from src import export_picklist_editor_csvs
import json

from unittest import mock
import pytest

import shutil
from unittest import mock

DATABASE = database.Database()


TEST_TIM_DATA = [
    {
        'auto_balls_low': 63,
        'auto_balls_high': 43,
        'tele_balls_low': 31,
        'tele_balls_high': 92,
        'control_panel_rotation': True,
        'control_panel_position': True,
        'incap': 42,
        'climb_time': 40,
        'confidence_rating': 88,
        'team_number': 0,
        'match_number': 1,
    },
    {
        'auto_balls_low': 6,
        'auto_balls_high': 75,
        'tele_balls_low': 22,
        'tele_balls_high': 44,
        'control_panel_rotation': False,
        'control_panel_position': False,
        'incap': 52,
        'climb_time': 50,
        'confidence_rating': 49,
        'team_number': 1661,
        'match_number': 1,
    },
]

TEST_TBA_DATA = [
    {
        'actual_time': 1583108484,
        'alliances': {
            'blue': {
                'dq_team_keys': [],
                'score': 192,
                'surrogate_team_keys': [],
                'team_keys': ['frc6560', 'frc115', 'frc114'],
            },
            'red': {
                'dq_team_keys': [],
                'score': 187,
                'surrogate_team_keys': [],
                'team_keys': ['frc1678', 'frc973', 'frc4'],
            },
        },
        'comp_level': 'f',
        'event_key': '2020caln',
        'key': '2020caln_f1m1',
        'match_number': 1,
        'post_result_time': 1583108789,
        'predicted_time': 1583108591,
        'score_breakdown': {
            'blue': {
                'adjustPoints': 0,
                'autoCellPoints': 54,
                'autoCellsBottom': 0,
                'autoCellsInner': 7,
                'autoCellsOuter': 3,
                'autoInitLinePoints': 15,
                'autoPoints': 69,
                'controlPanelPoints': 0,
                'endgamePoints': 55,
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'Park',
                'endgameRungIsLevel': 'NotLevel',
                'foulCount': 0,
                'foulPoints': 15,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankingPoint': False,
                'stage1Activated': True,
                'stage2Activated': False,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 2,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 0,
                'teleopCellPoints': 53,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 3,
                'teleopCellsOuter': 22,
                'teleopPoints': 108,
                'totalPoints': 192,
            },
            'red': {
                'adjustPoints': 0,
                'autoCellPoints': 74,
                'autoCellsBottom': 0,
                'autoCellsInner': 5,
                'autoCellsOuter': 11,
                'autoInitLinePoints': 15,
                'autoPoints': 89,
                'controlPanelPoints': 0,
                'endgamePoints': 50,
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'NotLevel',
                'foulCount': 0,
                'foulPoints': 0,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankingPoint': False,
                'stage1Activated': True,
                'stage2Activated': False,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 2,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 1,
                'teleopCellPoints': 48,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 0,
                'teleopCellsOuter': 24,
                'teleopPoints': 98,
                'totalPoints': 187,
            },
        },
        'set_number': 1,
        'time': 1583105760,
        'videos': [{'key': 'VYOLyHrfkVM', 'type': 'youtube'}],
        'winning_alliance': 'blue',
    },
    {
        'actual_time': 1583109581,
        'alliances': {
            'blue': {
                'dq_team_keys': [],
                'score': 177,
                'surrogate_team_keys': [],
                'team_keys': ['frc6560', 'frc115', 'frc114'],
            },
            'red': {
                'dq_team_keys': [],
                'score': 282,
                'surrogate_team_keys': [],
                'team_keys': ['frc1678', 'frc973', 'frc4'],
            },
        },
        'comp_level': 'f',
        'event_key': '2020caln',
        'key': '2020caln_f1m2',
        'match_number': 2,
        'post_result_time': 1583109855,
        'predicted_time': 1583109611,
        'score_breakdown': {
            'blue': {
                'adjustPoints': 0,
                'autoCellPoints': 58,
                'autoCellsBottom': 0,
                'autoCellsInner': 9,
                'autoCellsOuter': 1,
                'autoInitLinePoints': 15,
                'autoPoints': 73,
                'controlPanelPoints': 0,
                'endgamePoints': 35,
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Park',
                'endgameRobot3': 'Park',
                'endgameRungIsLevel': 'NotLevel',
                'foulCount': 1,
                'foulPoints': 6,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankingPoint': False,
                'stage1Activated': True,
                'stage2Activated': False,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 1,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 2,
                'teleopCellPoints': 63,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 11,
                'teleopCellsOuter': 15,
                'teleopPoints': 98,
                'totalPoints': 177,
            },
            'red': {
                'adjustPoints': 0,
                'autoCellPoints': 72,
                'autoCellsBottom': 0,
                'autoCellsInner': 6,
                'autoCellsOuter': 9,
                'autoInitLinePoints': 15,
                'autoPoints': 87,
                'controlPanelPoints': 10,
                'endgamePoints': 65,
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'IsLevel',
                'foulCount': 2,
                'foulPoints': 33,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankngPoint': False,
                'stage1Activated': True,
                'stage2Activated': True,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 2,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 0,
                'teleopCellPoints': 87,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 7,
                'teleopCellsOuter': 33,
                'teleopPoints': 162,
                'totalPoints': 282,
            },
        },
        'set_number': 1,
        'time': 1583106180,
        'videos': [{'key': 'CYg3fn30od8', 'type': 'youtube'}],
        'winning_alliance': 'red',
    },
    {
        'actual_time': 1583110694,
        'alliances': {
            'blue': {
                'dq_team_keys': [],
                'score': 158,
                'surrogate_team_keys': [],
                'team_keys': ['frc6560', 'frc115', 'frc114'],
            },
            'red': {
                'dq_team_keys': [],
                'score': 227,
                'surrogate_team_keys': [],
                'team_keys': ['frc1678', 'frc973', 'frc5089'],
            },
        },
        'comp_level': 'f',
        'event_key': '2020caln',
        'key': '2020caln_f1m3',
        'match_number': 3,
        'post_result_time': 1583110956,
        'predicted_time': 1583110752,
        'score_breakdown': {
            'blue': {
                'adjustPoints': 0,
                'autoCellPoints': 18,
                'autoCellsBottom': 0,
                'autoCellsInner': 1,
                'autoCellsOuter': 3,
                'autoInitLinePoints': 15,
                'autoPoints': 33,
                'controlPanelPoints': 0,
                'endgamePoints': 45,
                'endgameRobot1': 'None',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'Park',
                'endgameRungIsLevel': 'IsLevel',
                'foulCount': 0,
                'foulPoints': 30,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankingPoint': False,
                'stage1Activated': True,
                'stage2Activated': False,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 1,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 2,
                'teleopCellPoints': 50,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 8,
                'teleopCellsOuter': 13,
                'teleopPoints': 95,
                'totalPoints': 158,
            },
            'red': {
                'adjustPoints': 0,
                'autoCellPoints': 58,
                'autoCellsBottom': 0,
                'autoCellsInner': 5,
                'autoCellsOuter': 7,
                'autoInitLinePoints': 15,
                'autoPoints': 73,
                'controlPanelPoints': 10,
                'endgamePoints': 65,
                'endgameRobot1': 'Hang',
                'endgameRobot2': 'Hang',
                'endgameRobot3': 'None',
                'endgameRungIsLevel': 'IsLevel',
                'foulCount': 0,
                'foulPoints': 30,
                'initLineRobot1': 'Exited',
                'initLineRobot2': 'Exited',
                'initLineRobot3': 'Exited',
                'rp': 0,
                'shieldEnergizedRankingPoint': False,
                'shieldOperationalRankingPoint': False,
                'stage1Activated': True,
                'stage2Activated': True,
                'stage3Activated': False,
                'stage3TargetColor': 'Unknown',
                'tba_numRobotsHanging': 2,
                'tba_shieldEnergizedRankingPointFromFoul': False,
                'techFoulCount': 2,
                'teleopCellPoints': 49,
                'teleopCellsBottom': 0,
                'teleopCellsInner': 1,
                'teleopCellsOuter': 23,
                'teleopPoints': 124,
                'totalPoints': 227,
            },
        },
        'set_number': 1,
        'time': 1583106600,
        'videos': [{'key': 'Lc7jYFjoMm0', 'type': 'youtube'}],
        'winning_alliance': 'red',
    },
]


@pytest.fixture(autouse=True, scope="function")
def mock_team_list():
    with mock.patch.object(
        export_picklist_editor_csvs.BaseExport, "get_teams_list", return_value=[0, 1, 2, 3]
    ) as teams_list_mock:
        yield teams_list_mock


class TestBaseExport:
    def setup_method(self):
        self.base_class = export_picklist_editor_csvs.BaseExport()
        self.collections = self.base_class.collections
        self.teams_list = self.base_class.teams_list

    def test_load_single_collection(self):
        for collection in ["obj_tim", "subj_pit"]:
            result = self.base_class.load_single_collection(collection)
            assert isinstance(result, list)
            if len(result) > 0:
                assert isinstance(result[0], dict)

    def test_get_data(self):
        cols = ["obj_tim", "subj_pit"]
        result = self.base_class.get_data(cols)
        assert isinstance(result, dict)
        for key in ["obj_tim", "subj_pit"]:
            assert key in result

    def test_create_name(self):
        for name in ["endow", "tba_export"]:
            result_name = self.base_class.create_name(name)
            assert isinstance(result_name, str)

    def test_get_teams_list(self):
        result = self.base_class.get_teams_list()
        assert isinstance(result, list)
        assert result == self.teams_list


@pytest.fixture(autouse=True, scope="function")
def mock_tba_data():
    with mock.patch.object(
        export_picklist_editor_csvs.ExportTBA, "get_tba_data", return_value=TEST_TBA_DATA
    ) as teams_list_mock:
        yield teams_list_mock


class TestExportTBA:
    def setup_method(self):
        self.export_tba = export_picklist_editor_csvs.ExportTBA()

    def test_get_tba_data(self):
        result = self.export_tba.get_tba_data()
        assert isinstance(result, list)
        for single in result:
            assert isinstance(single["alliances"], dict)
            assert "red" in single["alliances"]
            assert "blue" in single["alliances"]
            assert isinstance(single["alliances"]["red"]["team_keys"], list)
            assert len(single["alliances"]["red"]["team_keys"]) == 3
            assert isinstance(single["event_key"], str)

    def test_build_data(self):
        result = self.export_tba.build_data()
        assert isinstance(result, list)


class TestExportTIM:
    def setup_method(self):
        self.export_tim = export_picklist_editor_csvs.ExportTIM()


class TestExportTeam:
    def setup_method(self):
        self.export_team = export_picklist_editor_csvs.ExportTeam()


class TestExportImagePaths:
    def setup_method(self):
        self.export_image_paths = export_picklist_editor_csvs.ExportImagePaths()

    def test_get_dict_for_teams(self):
        result = self.export_image_paths.get_dict_for_teams()
        assert isinstance(result, dict)

    def test_get_image_paths(self):
        result = self.export_image_paths.get_image_paths()
        assert isinstance(result, dict)
