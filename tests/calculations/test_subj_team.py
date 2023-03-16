#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
import pytest
from unittest.mock import patch
from calculations import subj_team
from server import Server


@pytest.mark.clouddb
class TestSubjTeamCalcs:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.test_calcs = subj_team.SubjTeamCalcs(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calcs.watched_collections == ["subj_tim"]
        assert self.test_calcs.server == self.test_server

    @staticmethod
    def near(num1, num2, max_diff=0.01) -> bool:
        return abs(num1 - num2) <= max_diff

    def test_teams_played_with(self):
        tims = [
            {
                "match_number": 1,
                "team_number": "1678",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "4414",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "1323",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 1,
                "team_number": "3",
                "alliance_color_is_red": False,
            },
            {
                "match_number": 2,
                "team_number": "4",
                "alliance_color_is_red": True,
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "alliance_color_is_red": False,
            },
            {
                "match_number": 3,
                "team_number": "2910",
                "alliance_color_is_red": False,
            },
        ]
        self.test_server.db.insert_documents("subj_tim", tims)
        assert self.test_calcs.teams_played_with("1678") == [
            "1678",
            "4414",
            "1323",
            "1678",
            "2910",
        ]

    def test_all_calcs(self):
        tims = [
            {
                "match_number": 1,
                "team_number": "118",
                "quickness_score": 2,
                "field_awareness_score": 1,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [2, 2, 2, 2],
            },
            {
                "match_number": 1,
                "team_number": "1678",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [1, 1, 0, 0],
            },
            {
                "match_number": 1,
                "team_number": "254",
                "quickness_score": 3,
                "field_awareness_score": 3,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [1, 1, 0, 0],
            },
            {
                "match_number": 2,
                "team_number": "118",
                "quickness_score": 2,
                "field_awareness_score": 1,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [2, 2, 2, 2],
            },
            {
                "match_number": 2,
                "team_number": "1678",
                "quickness_score": 3,
                "field_awareness_score": 3,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [1, 1, 1, 1],
            },
            {
                "match_number": 2,
                "team_number": "254",
                "quickness_score": 1,
                "field_awareness_score": 2,
                "alliance_color_is_red": True,
                "auto_pieces_start_position": [0, 0, 0, 0],
            },
            {
                "match_number": 3,
                "team_number": "118",
                "quickness_score": 1,
                "field_awareness_score": 3,
                "alliance_color_is_red": False,
                "auto_pieces_start_position": [0, 0, 1, 1],
            },
            {
                "match_number": 3,
                "team_number": "1678",
                "quickness_score": 2,
                "field_awareness_score": 2,
                "alliance_color_is_red": False,
                "auto_pieces_start_position": [1, 1, 0, 1],
            },
            {
                "match_number": 3,
                "team_number": "254",
                "quickness_score": 1,
                "field_awareness_score": 3,
                "alliance_color_is_red": False,
                "auto_pieces_start_position": [0, 1, 0, 0],
            },
        ]
        self.test_server.db.delete_data("subj_tim")
        self.test_server.db.insert_documents("subj_tim", tims)
        self.test_calcs.run()
        robonauts = self.test_server.db.find("subj_team", {"team_number": "118"})[0]
        citrus = self.test_server.db.find("subj_team", {"team_number": "1678"})[0]
        chezy = self.test_server.db.find("subj_team", {"team_number": "254"})[0]

        assert self.near(robonauts["driver_field_awareness"], 0.9259)
        assert self.near(robonauts["driver_quickness"], 0.55555)
        assert self.near(robonauts["driver_ability"], 0.65632)
        for i in range(4):
            assert self.near(robonauts["auto_pieces_start_position"][i], [0, 0, 1, 1][i])

        assert self.near(citrus["driver_field_awareness"], 1.296)
        assert self.near(citrus["driver_quickness"], 0.666667)
        assert self.near(citrus["driver_ability"], 3.053327)
        for i in range(4):
            assert self.near(citrus["auto_pieces_start_position"][i], [1, 1, 0.333333, 0.666666][i])

        assert self.near(chezy["driver_field_awareness"], 1.481)
        assert self.near(chezy["driver_quickness"], 0.555555)
        assert self.near(chezy["driver_ability"], 2.29057)
        for i in range(4):
            assert self.near(chezy["auto_pieces_start_position"][i], [0.333333, 0.666666, 0, 0][i])
