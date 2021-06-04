#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
import pytest
from src.calculations import subj_team
from src.server import Server


@pytest.mark.clouddb
class TestSubjTeamCalcs:
    def setup_method(self, method):
        self.test_server = Server()
        self.test_calcs = subj_team.SubjTeamCalcs(self.test_server)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calcs.watched_collections == ['subj_aim']
        assert self.test_calcs.server == self.test_server

    @staticmethod
    def near(num1, num2, max_diff=0.01) -> bool:
        return abs(num1 - num2) <= max_diff

    def test_teams_played_with(self):
        aims = [
            {'agility_rankings': [1, 1678, 2]},
            {'agility_rankings': [2, 1678, 3]},
            {'agility_rankings': [1, 3, 4]},
        ]
        self.test_server.db.insert_documents('subj_aim', aims)
        assert self.test_calcs.teams_played_with(1678) == [1, 1678, 2, 2, 1678, 3]

    def test_all_calcs(self):
        aims = [
            {'agility_rankings': [118, 1678, 254], 'rendezvous_agility_rankings': [254, 118, 1678]},
            {'agility_rankings': [1678, 118, 254], 'rendezvous_agility_rankings': [118, 254, 1678]},
        ]
        self.test_server.db.insert_documents('subj_aim', aims)
        self.test_calcs.run()
        robonauts = self.test_server.db.find('subj_team', team_number=118)[0]
        citrus = self.test_server.db.find('subj_team', team_number=1678)[0]
        chezy = self.test_server.db.find('subj_team', team_number=254)[0]

        assert self.near(robonauts['driver_agility'], -0.71)
        assert self.near(robonauts['driver_rendezvous_agility'], -0.71)
        assert self.near(robonauts['driver_ability'], -0.29)

        assert self.near(citrus['driver_agility'], -0.71)
        assert self.near(citrus['driver_rendezvous_agility'], 1.41)
        assert self.near(citrus['driver_ability'], -0.12)

        assert self.near(chezy['driver_agility'], 1.41)
        assert self.near(chezy['driver_rendezvous_agility'], -0.71)
        assert self.near(chezy['driver_ability'], 0.41)
