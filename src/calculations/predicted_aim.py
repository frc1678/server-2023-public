#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import server
import dataclasses
import math
from calculations.base_calculations import BaseCalculations


@dataclasses.dataclass
class PredictedAimScores:
    auto_balls_low: float = 0.0
    auto_balls_outer: float = 0.0
    auto_balls_inner: float = 0.0
    tele_balls_low: float = 0.0
    tele_balls_outer: float = 0.0
    tele_balls_inner: float = 0.0
    auto_line_success_rate: float = 0.0
    rotation_success_rate: int = 0
    position_success_rate: int = 0
    climb_success_rate: float = 0.0
    park_success_rate: float = 0.0


class PredictedAimCalc(BaseCalculations):
    ROTATION_THRESHOLD = 24
    POSITION_THRESHOLD = 39
    ENDGAME_RP_THRESHOLD = 65
    POINTS = {
        'auto_balls_low': 2,
        'auto_balls_outer': 4,
        'auto_balls_inner': 6,
        'tele_balls_low': 1,
        'tele_balls_outer': 2,
        'tele_balls_inner': 3,
        'auto_line_success_rate': 5,
        'rotation_success_rate': 15,
        'position_success_rate': 20,
        'climb_success_rate': 25,
        'park_success_rate': 5,
        'level_bonus': 15,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ['obj_team', 'tba_team']

    def calculate_stage_contribution(self, predicted_values):
        """Determines how many balls an alliance will contribute towards stage thresholds.

        Used for predicting control panel points.
        predicted_values is a dataclass which stores the predicted number of balls scored and success rates."""
        predicted_values = dataclasses.asdict(predicted_values)

        auto_balls = sum(
            [value for field, value in predicted_values.items() if 'auto_balls' in field]
        )
        # The max number of balls in auto that count towards the threshold is 9. Takes the lower value between
        # the number of balls scored in auto and 9.
        total_balls = min((auto_balls, 9))

        # No limit on tele balls, add all tele balls
        total_balls += sum(
            [value for field, value in predicted_values.items() if 'tele_balls' in field]
        )

        return total_balls

    def calculate_predicted_balls_score(self, predicted_values, obj_team, tba_team):
        """Calculates the predicted score from balls.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data.
        The value of [stage]_balls_percent_inner is a decimal between 1 and 0."""
        # Find the predicted balls scored in auto
        predicted_values.auto_balls_low += obj_team['auto_avg_balls_low']
        predicted_values.auto_balls_inner += (
            obj_team['auto_avg_balls_high'] * tba_team['auto_high_balls_percent_inner']
        )
        predicted_values.auto_balls_outer += obj_team['auto_avg_balls_high'] * (
            1 - tba_team['auto_high_balls_percent_inner']
        )

        # Find the predicted balls scored in tele
        predicted_values.tele_balls_low += obj_team['tele_avg_balls_low']
        predicted_values.tele_balls_inner += (
            obj_team['tele_avg_balls_high'] * tba_team['tele_high_balls_percent_inner']
        )
        predicted_values.tele_balls_outer += obj_team['tele_avg_balls_high'] * (
            1 - tba_team['tele_high_balls_percent_inner']
        )

    def calculate_predicted_panel_score(self, predicted_values, obj_team):
        """Calculates the predicted score from the control panel.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        Control panel success rate represents whether or not a team has demonstrated control panel ability at all in the past,
        not a real success rate. This is so that we don't underestimate because the control panel is rarely used."""
        if obj_team['tele_cp_rotation_successes'] > 0:
            predicted_values.rotation_success_rate = 1

        if obj_team['tele_cp_position_successes'] > 0:
            predicted_values.position_success_rate = 1

    def calculate_predicted_alliance_score(
        self, predicted_values, obj_team_data, tba_team_data, team_numbers
    ):
        """Calculates the predicted score for an alliance.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data.
        team_numbers is a list of team numbers (integers) on the alliance.
        """

        total_score = 0

        for team in team_numbers:
            obj_team = [
                team_data for team_data in obj_team_data if team_data['team_number'] == team
            ][0]
            tba_team = [
                team_data for team_data in tba_team_data if team_data['team_number'] == team
            ][0]

            self.calculate_predicted_balls_score(predicted_values, obj_team, tba_team)
            self.calculate_predicted_panel_score(predicted_values, obj_team)

            # Calculates rates of success for auto line, climb, and park out of all matches played
            # Doesn't use climb_percent_success because it is calculated out of climb attempts, not matches played
            predicted_values.auto_line_success_rate += (
                tba_team['auto_line_successes'] / obj_team['matches_played']
            )
            predicted_values.climb_success_rate += (
                tba_team['climb_all_successes'] / obj_team['matches_played']
            )
            predicted_values.park_success_rate += (
                tba_team['park_successes'] / obj_team['matches_played']
            )

        # Finds which stages the alliance has reached to determine eligibility for control panel points
        threshold_contribution = self.calculate_stage_contribution(predicted_values)

        for data_field in dataclasses.asdict(predicted_values).keys():
            if data_field == 'rotation_success_rate':
                if threshold_contribution >= self.ROTATION_THRESHOLD:
                    total_score += (
                        predicted_values.rotation_success_rate
                        * self.POINTS['rotation_success_rate']
                    )
            elif data_field == 'position_success_rate':
                if threshold_contribution >= self.POSITION_THRESHOLD:
                    total_score += (
                        predicted_values.position_success_rate
                        * self.POINTS['position_success_rate']
                    )
            elif data_field == 'climb_success_rate':
                # Round to the nearest whole number of climbs (rounds up on a .5, cancels out parks rounding down)
                num_climbs = math.floor(predicted_values.climb_success_rate + 0.5)
                # If there are more than 2 climbs, assume balanced climb
                if num_climbs >= 2:
                    total_score += self.POINTS['level_bonus']
                total_score += num_climbs * self.POINTS['climb_success_rate']
            elif data_field == 'park_success_rate':
                # Round to the nearest whole number of parks (rounds down on a .5, cancels out climbs rounding up)
                total_score += (
                    math.ceil(predicted_values.park_success_rate - 0.5)
                    * self.POINTS['park_success_rate']
                )
            else:
                total_score += getattr(predicted_values, data_field) * self.POINTS[data_field]

        return total_score

    def calculate_predicted_climb_rp(self, predicted_values):
        """Calculates whether an alliance is expected to earn the endgame RP.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        """
        endgame_score = 0
        endgame_score += (
            math.floor(predicted_values.climb_success_rate + 0.5)
            * self.POINTS['climb_success_rate']
        )
        # If there are more than 2 climbs, assume balanced climb
        if endgame_score >= self.POINTS['climb_success_rate'] * 2:
            endgame_score += self.POINTS['level_bonus']
        endgame_score += (
            math.ceil(predicted_values.park_success_rate - 0.5) * self.POINTS['park_success_rate']
        )

        if endgame_score >= self.ENDGAME_RP_THRESHOLD:
            return 1.0
        return 0.0

    def calculate_predicted_stage_rp(self, predicted_values):
        """Calculates whether an alliance is expected to earn the stage RP.

        Alliances earn the stage RP automatically if they reach the point threshold becuase past panel performance
        is not the best predictor.
        predicted_values is a dataclass which stores the predicted number of balls scored and success rates."""
        if self.calculate_stage_contribution(predicted_values) >= self.POSITION_THRESHOLD:
            return 1.0
        return 0.0

    def filter_aims_list(self, obj_team, tba_team, aims_list):
        """Filters the aims list to only contain aims where all teams have existing data.

        Prevents predictions from crashing due to being run on teams with no data.
        obj_team is all the obj_team data in the database. tba_team is all the tba_team data in the database.
        aims_list is all the aims before filtering."""
        filtered_aims_list = []

        # List of all teams that have existing documents in obj_team and tba_team
        obj_team_numbers = [team_data['team_number'] for team_data in obj_team]
        tba_team_numbers = [team_data['team_number'] for team_data in tba_team]

        for aim in aims_list:
            has_data = True
            for team in aim['team_list']:
                # has_data is False if any of the teams in the aim are missing obj_team or tba_team data
                if team not in obj_team_numbers or team not in tba_team_numbers:
                    has_data = False
                    utils.log_warning(
                        f'Incomplete team data for Alliance {aim["alliance_color"]} in Match {aim["match_number"]}'
                    )
                    break
            if has_data == True:
                filtered_aims_list.append(aim)

        return filtered_aims_list

    def update_predicted_aim(self, aims_list):
        updates = []
        obj_team = self.server.db.find('obj_team')
        tba_team = self.server.db.find('tba_team')

        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        for aim in filtered_aims_list:
            predicted_values = PredictedAimScores()
            update = {
                'match_number': aim['match_number'],
                'alliance_color_is_red': aim['alliance_color'] == 'R',
            }
            update['predicted_score'] = self.calculate_predicted_alliance_score(
                predicted_values, obj_team, tba_team, aim['team_list']
            )
            update['predicted_rp1'] = self.calculate_predicted_climb_rp(predicted_values)
            update['predicted_rp2'] = self.calculate_predicted_stage_rp(predicted_values)
            updates.append(update)
        return updates

    def run(self):
        # Get oplog entries
        entries = self.entries_since_last()
        teams = set()
        match_schedule = self._get_aim_list()
        # Check if changes need to be made to teams
        if self.entries_since_last() is not None:
            for entry in entries:
                # Prevents error from not having a team num
                if 'team_number' in entry['o'].keys():
                    teams.add(entry['o']['team_number'])
        aims = []
        for alliance in match_schedule:
            for team in alliance['team_list']:
                if team in teams:
                    aims.append(alliance)
                    break
        for update in self.update_predicted_aim(aims):
            self.server.db.update_document(
                'predicted_aim',
                update,
                {
                    'match_number': update['match_number'],
                    'alliance_color_is_red': update['alliance_color_is_red'],
                },
            )
