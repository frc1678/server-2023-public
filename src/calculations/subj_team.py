#!/usr/bin/env python3
"""Calculate subjective team data"""

import utils
from calculations import base_calculations
from typing import Dict, List


class SubjTeamCalcs(base_calculations.BaseCalculations):
    """Runs subjective team calculations"""

    SCHEMA = utils.read_schema('schema/calc_subj_team_schema.yml')

    def __init__(self, server):
        """Overrides watched collections, passes server object"""
        super().__init__(server)
        self.watched_collections = ['subj_aim']
        self.teams_that_have_competed = set()

    def teams_played_with(self, team: int) -> List[int]:
        """Returns a list of teams that the given team has played with so far, including themselves
        and including repeats"""
        partners = []
        for aim in self.server.db.find('subj_aim'):
            if team in aim['near_field_awareness_rankings']:
                partners += aim['near_field_awareness_rankings']
        return partners

    def unadjusted_ability_calcs(self, team: int) -> Dict[str, float]:
        """Retrieves subjective AIM info for the given team and returns a dictionary with
        calculations for that team"""
        calculations = {}
        # self.SCHEMA['data'] tells us which fields we need to put in the database that don't
        # require calculations
        for data_field, type_as_str in self.SCHEMA['data'].items():
            if data_field == 'team_number':
                calculations[data_field] = self.STR_TYPES[type_as_str](team)
            else:
                raise Exception(f"Schema mentions {data_field} but we don't know what that is")
        # Next, actually run the calculations
        for calc_name, calc_info in self.SCHEMA['calculations'].items():
            if [datafield for datafield in calc_info['requires'] if 'subj_aim.' not in datafield]:
                # If this calculation depends on data from another collection, skip it for now, and
                # another function will handle it
                continue
            # For calculations such as driver_field_awareness and driver_quickness,
            # we just pull the rankings from the database and normalize them
            collection_name, _, ranking_name = calc_info['requires'][0].partition('.')
            subj_aim_data = [aim[ranking_name] for aim in self.server.db.find(collection_name)]
            # Ethan and Nathan were here :)
            rankings = {}
            for team_list in subj_aim_data:
                # team_list is an ordered list of the team numbers in the AIM
                # Their position in that list indicates their ranking (index 0 is worst)
                for rank, team_num in enumerate(team_list):
                    rankings[team_num] = rankings.get(team_num, []) + [rank]
            # Python3.8 should preserve the order of keys & values when doing weird stuff like this
            average_team_rankings = [self.avg(team_rankings) for team_rankings in rankings.values()]
            normalized_rankings = dict(
                zip(rankings.keys(), self.get_z_scores(average_team_rankings))
            )
            calculations[calc_name] = normalized_rankings[team]
        return calculations

    def adjusted_ability_calcs(self) -> Dict[str, Dict[int, float]]:
        """Retrieves subjective AIM data for all teams and recalculates adjusted ability scores
        for each team. Recalculating all of them is necessary because driver_ability compensates for
        luck of match schedule, so a team's driver ability score will depend on the unadjusted
        scores for all of their alliance partners"""
        calculations = {}
        for calc_name, calc_info in self.SCHEMA['calculations'].items():
            # The only calculation we want to run here is the one that depends only on subjective
            # team data we've already calculated
            if [datafield for datafield in calc_info['requires'] if 'subj_team.' not in datafield]:
                continue
            composite_scores = {}
            for team in self.teams_that_have_competed:
                # scores is a list of the normalized subjective ability scores for the team
                # For example, if they have good driver_field_awareness and average
                # driver_quickness, scores might look like [.8, -.3]
                scores = []
                for requirement in calc_info['requires']:
                    collection_name, _, score_name = requirement.partition('.')
                    scores.append(
                        self.server.db.find(collection_name, team_number=team)[0][score_name]
                    )
                composite_scores[team] = self.avg(scores, calc_info['weights'])
            # Now scale the scores so they range from 0 to 1, and use those scaled scores to
            # compensate for alliance partners
            # That way, teams that are always paired with good/bad teams won't have unfair rankings
            worst = min(composite_scores.values())
            best = max(composite_scores.values())
            scaled_scores = {
                team: (score - worst) / (best - worst) for team, score in composite_scores.items()
            }
            adjusted_scores = {}
            for team, score in composite_scores.items():
                teammate_scaled_scores = [
                    scaled_scores[partner] for partner in self.teams_played_with(team)
                ]
                calculations[team] = calculations.get(team, {})
                calculations[team][calc_name] = score * self.avg(teammate_scaled_scores)
        return calculations

    def run(self):
        """Gets oplog entries from watched collection and uses that to calculate subjective team
        info, then puts those calculations in the database"""
        self.teams_that_have_competed = set()
        for aim in self.server.db.find('subj_aim'):
            self.teams_that_have_competed.update(aim['near_field_awareness_rankings'])
        # See which teams are affected by new subj AIM data
        entries = self.entries_since_last()
        teams = set()
        if self.entries_since_last() is not None:
            for entry in entries:
                teams.update(entry['o']['near_field_awareness_rankings'])
        for team in teams:
            new_calc = self.unadjusted_ability_calcs(team)
            self.server.db.update_document(
                'subj_team', new_calc, {'team_number': new_calc['team_number']}
            )
        # Now use the new info to recalculate adjusted ability scores
        adjusted_calcs = self.adjusted_ability_calcs()
        for team in self.teams_that_have_competed:
            self.server.db.update_document('subj_team', adjusted_calcs[team], {'team_number': team})
