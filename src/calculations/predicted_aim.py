#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import dataclasses

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator


@dataclasses.dataclass
class PredictedAimScores:
    auto_cube_low: float = 0.0
    auto_cube_mid: float = 0.0
    auto_cube_high: float = 0.0
    auto_cone_low: float = 0.0
    auto_cone_mid: float = 0.0
    auto_cone_high: float = 0.0
    auto_dock: float = 0.0
    auto_engage: float = 0.0
    mobility: float = 0.0
    tele_cube_low: float = 0.0
    tele_cube_mid: float = 0.0
    tele_cube_high: float = 0.0
    tele_cone_low: float = 0.0
    tele_cone_mid: float = 0.0
    tele_cone_high: float = 0.0
    tele_dock: float = 0.0
    tele_park: float = 0.0
    tele_engage: float = 0.0


class PredictedAimCalc(BaseCalculations):
    POINTS = {
        "auto_cube_low": 3,
        "auto_cube_mid": 4,
        "auto_cube_high": 6,
        "auto_cone_low": 3,
        "auto_cone_mid": 4,
        "auto_cone_high": 6,
        "auto_dock": 8,
        "auto_engage": 12,
        "mobility": 3,
        "tele_cube_low": 2,
        "tele_cube_mid": 3,
        "tele_cube_high": 5,
        "tele_cone_low": 2,
        "tele_cone_mid": 3,
        "tele_cone_high": 5,
        "tele_dock": 6,
        "tele_park": 2,
        "tele_engage": 10,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    # def calculate_predicted_sustainability_threshold(self, obj_team):
    # TBA

    def calculate_predicted_charge_success_rate(self, predicted_values, obj_team):
        predicted_values.team_attempts += (
            obj_team["auto_charge_attempts"] + obj_team["tele_charge_attempts"]
        )
        predicted_values.team_dock_success_rate += (
            obj_team["auto_dock"] + obj_team["tele_dock"]
        ) / predicted_values.team_attempts
        predicted_values.team_engage_successes_rate += (
            obj_team["auto_engage"] + obj_team["tele_engage"]
        ) / predicted_values.team_attempts
        predicted_values.team_park_success_rate += (
            obj_team["tele_park"] / obj_team["tele_charge_attempts"]
        )

    def calculate_predicted_grid_score(self, predicted_values, obj_team):
        """Calculates the predicted score from grid.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data.
        The value of [stage]_balls_percent_inner is a decimal between 1 and 0."""
        # Finds the predicted cubes scored in auto
        predicted_values.auto_cube_low += obj_team["auto_avg_cube_low"]
        predicted_values.auto_cube_mid += obj_team["auto_avg_cube_mid"]
        predicted_values.auto_cube_high += obj_team["auto_avg_cube_high"]

        # Finds the predicted cones scored in auto
        predicted_values.auto_cone_low += obj_team["auto_avg_cone_low"]
        predicted_values.auto_cone_mid += obj_team["auto_avg_cone_mid"]
        predicted_values.auto_cone_high += obj_team["auto_avg_cone_high"]

        # Finds the predicted cubes scored in tele
        predicted_values.tele_cube_low += obj_team["tele_avg_cube_low"]
        predicted_values.tele_cube_mid += obj_team["tele_avg_cube_mid"]
        predicted_values.tele_cube_high += obj_team["tele_avg_cube_high"]

        # Finds the predicted cones score in tele
        predicted_values.tele_cone_low += obj_team["tele_avg_cone_low"]
        predicted_values.tele_cone_low += obj_team["tele_avg_cone_mid"]
        predicted_values.tele_cone_low += obj_team["tele_avg_cone_high"]

    def calculate_predicted_alliance_score(
        self, predicted_values, obj_team_data, tba_team_data, team_numbers
    ):
        """Calculates the predicted score for an alliance.

        predicted_values is a dataclass which stores the predicted number of cones/cubes scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data.
        team_numbers is a list of team numbers (strings) on the alliance.
        """

        total_score = 0

        for team in team_numbers:
            obj_team = [
                team_data for team_data in obj_team_data if team_data["team_number"] == team
            ][0]
            tba_team = [
                team_data for team_data in tba_team_data if team_data["team_number"] == team
            ][0]

            self.calculate_predicted_grid_score(predicted_values, obj_team)
            self.calculate_predicted_charge_success_rate(predicted_values, obj_team)

        for data_field in dataclasses.asdict(predicted_values).keys():
            total_score += getattr(predicted_values, data_field) * self.POINTS[data_field]

        return total_score

    def calculate_predicted_charge_rp(self, predicted_values):
        """Calculates whether an alliance is expected to earn the endgame RP.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        """
        charge_score = 0
        charge_score += predicted_values.team_dock_success_rate * (
            self.POINTS["auto_dock"] + self.POINTS["tele_dock"]
        ) + predicted_values.team_engage_success_rate * (
            self.POINTS["auto_engage"] + self.POINTS["tele_engage"]
        )

        if charge_score >= 26:
            return 1.0
        return 0.0

        # def calculate_predicted_ball_rp(self, obj_team, predicted_values):
        cargo_rp_threshold = self.calculate_predicted_quintet_success(obj_team)
        balls_scored = (
            predicted_values.auto_low_balls
            + predicted_values.auto_high_balls
            + predicted_values.tele_low_balls
            + predicted_values.tele_high_balls
        )
        if balls_scored >= cargo_rp_threshold:
            return 1.0
        return 0.0
        # TBA

        # def get_actual_values(self, aim, tba_match_data):
        """Pulls actual AIM data from TBA if it exists.

        Otherwise, returns dictionary with all values of 0 and has_actual_data of False.
        aim is the alliance in match to pull actual data for."""
        actual_match_dict = {
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
            "has_actual_data": False,
        }
        match_number = aim["match_number"]

        for match in tba_match_data:
            # Checks the value of winning_alliance to determine if the match has data.
            # If there is no data for the match, winning_alliance is an empty string.
            if (
                match["match_number"] == match_number
                and match["comp_level"] == "qm"
                and match["post_result_time"] != None
            ):
                actual_aim = match["score_breakdown"]
                if aim["alliance_color"] == "R":
                    alliance_color = "red"
                else:
                    alliance_color = "blue"
                actual_match_dict["actual_score"] = actual_aim[alliance_color]["totalPoints"]
                # TBA stores RPs as booleans. If the RP is true, they get 1 RP, otherwise they get 0.
                if actual_aim[alliance_color]["cargoBonusRankingPoint"]:
                    actual_match_dict["actual_rp1"] = 1.0
                if actual_aim[alliance_color]["hangarBonusRankingPoint"]:
                    actual_match_dict["actual_rp2"] = 1.0
                # Gets whether the alliance won the match by checking the winning alliance against the alliance color/
                actual_match_dict["won_match"] = match["winning_alliance"] == alliance_color
                # Sets actual_match_data to true once the actual data has been pulled
                actual_match_dict["has_actual_data"] = True
                break

        return actual_match_dict

    def filter_aims_list(self, obj_team, tba_team, aims_list):
        """Filters the aims list to only contain aims where all teams have existing data.

        Prevents predictions from crashing due to being run on teams with no data.
        obj_team is all the obj_team data in the database. tba_team is all the tba_team data in the database.
        aims_list is all the aims before filtering."""
        filtered_aims_list = []

        # List of all teams that have existing documents in obj_team and tba_team
        obj_team_numbers = [team_data["team_number"] for team_data in obj_team]
        tba_team_numbers = [team_data["team_number"] for team_data in tba_team]

        for aim in aims_list:
            has_data = True
            for team in aim["team_list"]:
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
        obj_team = self.server.db.find("obj_team")
        tba_team = self.server.db.find("tba_team")
        tba_match_data = tba_communicator.tba_request(f"event/{self.server.TBA_EVENT_KEY}/matches")

        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        for aim in filtered_aims_list:
            predicted_values = PredictedAimScores()
            update = {
                "match_number": aim["match_number"],
                "alliance_color_is_red": aim["alliance_color"] == "R",
            }
            update["predicted_score"] = self.calculate_predicted_alliance_score(
                predicted_values, obj_team, tba_team, aim["team_list"]
            )
            update["predicted_rp1"] = self.calculate_predicted_ball_rp(obj_team, predicted_values)
            update["predicted_rp2"] = self.calculate_predicted_climb_rp(predicted_values)
            update.update(self.get_actual_values(aim, tba_match_data))
            updates.append(update)
        return updates

    def calculate_predicted_win_chance(self):
        new_aims = []
        aims = self.server.db.find("predicted_aim")
        match_list = set([aim["match_number"] for aim in aims])
        for match in match_list:
            aims_in_match = [aim for aim in aims if aim["match_number"] == match]
            if len(aims_in_match) < 2:
                break
            for aim in range(2):
                aim_score = aims_in_match[aim]["predicted_score"]
                opponent_score = aims_in_match[(aim + 1) % 2]["predicted_score"]
                aims_in_match[aim]["win_chance"] = 0.5 + ((aim_score - opponent_score) * 0.0227)
                new_aims.append(aims_in_match[aim])
        return new_aims

    def run(self):
        match_schedule = self.get_aim_list()
        # Check if changes need to be made to teams
        teams = self.get_updated_teams()
        aims = []
        for alliance in match_schedule:
            for team in alliance["team_list"]:
                if team in teams:
                    aims.append(alliance)
                    break
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("predicted_aim")

        for update in self.update_predicted_aim(aims):
            self.server.db.update_document(
                "predicted_aim",
                update,
                {
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )

        for update in self.calculate_predicted_win_chance():
            self.server.db.update_document(
                "predicted_aim",
                update,
                {
                    "match_number": update["match_number"],
                    "alliance_color_is_red": update["alliance_color_is_red"],
                },
            )
