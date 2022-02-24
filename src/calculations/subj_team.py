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
        self.watched_collections = ['subj_tim']
        self.teams_that_have_competed = set()

    def teams_played_with(self, team: int) -> List[int]:
        """Returns a list of teams that the given team has played with so far, including themselves
        and including repeats"""
        partners = []
        # matches_played is a dictionary where keys are match numbers and values represent alliance color
        matches_played = {}
        for tim in self.server.db.find('subj_tim', team_number=team):
            matches_played.update({tim['match_number']: tim['alliance_color_is_red']})
        for match_num, alliance_color in matches_played.items():
            # Find subj_tim data for robots in the same match and alliance as the team
            alliance_data = self.server.db.find('subj_tim', match_number=match_num, alliance_color_is_red=alliance_color)
            partners.extend([tim['team_number'] for tim in alliance_data])
        return partners

    def unadjusted_ability_calcs(self, team: int) -> Dict[str, float]:
        """Retrieves subjective AIM info for the given team and returns a dictionary with
        calculations for that team"""
        calculations = {}
        # self.SCHEMA['data'] tells us which fields we need to put in the database that don't
        # require calculations
        for data_field, type_dict in self.SCHEMA['data'].items():
            type_as_str = type_dict['type']
            if data_field == 'team_number':
                calculations[data_field] = self.STR_TYPES[type_as_str](team)
            else:
                raise Exception(f"Schema mentions {data_field} but we don't know what that is")
        # Next, actually run the calculations
        for calc_name, calc_info in self.SCHEMA['unadjusted_calculations'].items():
            collection_name, _, ranking_name = calc_info['requires'][0].partition('.')
            # For calculations such as driver_field_awareness and driver_quickness,
            # we just pull the rankings from the database and average them
            # Ethan and Nathan were here :)
            team_rankings = [tim[ranking_name] for tim in self.server.db.find(collection_name, team_number=team)]
            average_team_rankings = self.avg(team_rankings)
            calculations[calc_name] = average_team_rankings
        return calculations

    def adjusted_ability_calcs(self) -> Dict[str, Dict[int, float]]:
        """Retrieves subjective AIM data for all teams and recalculates adjusted ability scores
        for each team. Recalculating all of them is necessary because ability scores compensate for
        luck of match schedule, so a team's ability score will depend on the unadjusted
        scores for all of their alliance partners"""
        calculations = {}
        for calc_name, calc_info in self.SCHEMA['component_calculations'].items():
            collection_name, _, unadjusted_calc = calc_info['requires'][0].partition('.')
            # scores is a dictionary of team numbers to rank score
            scores = {}
            for team in self.teams_that_have_competed:
                score = self.server.db.find(collection_name, team_number=team)[0][unadjusted_calc]
                scores[team] = score
            # Now scale the scores so they range from 0 to 1, and use those scaled scores to
            # compensate for alliance partners
            # That way, teams that are always paired with good/bad teams won't have unfair rankings
            worst = min(scores.values())
            best = max(scores.values())
            scaled_scores = {team: (score - worst) / (best - worst) for team, score in scores.items()}
            for team, score in scores.items():
                teammate_scaled_scores = [scaled_scores[partner] for partner in self.teams_played_with(team)]
                calculations[team] = calculations.get(team, {})
                # If teammates tend to rank low, the team's score is lowered more than if teammates tend to rank high
                calculations[team][calc_name] = score * self.avg(teammate_scaled_scores)
        return calculations

    def calculate_driver_ability(self):
        """Takes a weighted average of all the adjusted component scores to calculate overall driver ability."""
        calculations = {}
        for calc_name, calc_info in self.SCHEMA['averaged_calculations'].items():
            # ability_dict is a dictionary where keys are team numbers
            # and values are driver_ability scores
            ability_dict = {}
            for team in self.teams_that_have_competed:
                # scores is a list of the normalized, adjusted subjective ability scores for the team
                # For example, if they have good quickness and average
                # field awareness, scores might look like [.8, -.3]
                scores = []
                for requirement in calc_info['requires']:
                    collection_name, _, score_name = requirement.partition('.')
                    scores.append(
                        self.server.db.find(collection_name, team_number=team)[0][score_name]
                    )
                # driver_ability is a weighted average of its component scores
                ability_dict[team] = self.avg(scores, calc_info['weights'])
            # Put the driver abilities of all teams in a list
            driver_ability_list = [ability for ability in ability_dict.values()]
            normalized_abilities = dict(zip(ability_dict.keys(), self.get_z_scores(driver_ability_list)))
            for team, driver_ability in normalized_abilities.items():
                calculations[team] = calculations.get(team, {})
                # Add 2 to driver ability in order to move the lowest scores closer to 0 instead of negative
                calculations[team][calc_name] = driver_ability + 2
        return calculations

    def calculate_ratings(self, team):
        """Calculates rating datapoints, which aren't rankings."""
        calculations = {}
        for calc_name, calc_info in self.SCHEMA['ratings'].items():
            for requirement in calc_info['requires']:
                collection_name, _, rating_name = requirement.partition('.')
                # Filter out all values of 0 (when the team didn't perform the ranked action)
                tim_ratings = [tim[rating_name] for tim in self.server.db.find(collection_name, team_number=team) if tim[rating_name] != 0]
                calculations[calc_name] = self.avg(tim_ratings)
        return calculations

    def run(self):
        """Gets oplog entries from watched collection and uses that to calculate subjective team
        info, then puts those calculations in the database"""
        # Adjusted calcs have to be re-run on all teams that have competed
        # because team data changing for one team affects all teams that played with that team
        self.teams_that_have_competed = set()
        for tim in self.server.db.find('subj_tim'):
            self.teams_that_have_competed.add(tim['team_number'])
        # See which teams are affected by new subj TIM data
        entries = self.entries_since_last()
        updated_teams = self.find_team_list()
        for team in updated_teams:
            new_calc = self.unadjusted_ability_calcs(team)
            new_calc.update(self.calculate_ratings(team))
            self.server.db.update_document(
                'subj_team', new_calc, {'team_number': new_calc['team_number']}
            )
        # Now use the new info to recalculate adjusted ability scores
        adjusted_calcs = self.adjusted_ability_calcs()
        for team in self.teams_that_have_competed:
            self.server.db.update_document('subj_team', adjusted_calcs[team], {'team_number': team})
        # Use the adjusted ability scores to calculate driver ability
        driver_ability_calcs = self.calculate_driver_ability()
        for team in self.teams_that_have_competed:
            self.server.db.update_document('subj_team', driver_ability_calcs[team], {'team_number': team})
