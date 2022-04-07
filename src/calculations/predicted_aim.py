#!/usr/bin/env python3
"""Makes predictive calculations for alliances in matches in a competition."""

import utils
import server
import dataclasses
import math

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator


@dataclasses.dataclass
class PredictedAimScores:
    auto_low_balls: float = 0.0
    auto_high_balls: float = 0.0
    tele_low_balls: float = 0.0
    tele_high_balls: float = 0.0
    auto_line_success_rate: float = 0.0
    low_rung_success_rate: float = 0.0
    mid_rung_success_rate: float = 0.0
    high_rung_success_rate: float = 0.0
    traversal_rung_success_rate: float = 0.0


class PredictedAimCalc(BaseCalculations):
    ENDGAME_CLIMB_THRESHOLD = 16
    POINTS = {
        "auto_low_balls": 2,
        "auto_high_balls": 4,
        "tele_low_balls": 1,
        "tele_high_balls": 2,
        "auto_line_success_rate": 2,
        "low_rung_success_rate": 4,
        "mid_rung_success_rate": 6,
        "high_rung_success_rate": 10,
        "traversal_rung_success_rate": 15,
    }

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["obj_team", "tba_team"]

    def calculate_predicted_quintet_success(self, obj_team):
        auto_balls_scored = 0
        auto_balls_scored += sum([team["auto_avg_total_balls"] for team in obj_team])

        if auto_balls_scored <= 4:
            cargo_rp_threshold = 20
        elif auto_balls_scored < 5:
            cargo_rp_threshold = 19
        else:
            cargo_rp_threshold = 18

        return cargo_rp_threshold

    def calculate_predicted_climb_success_rate(self, predicted_values, obj_team):
        predicted_values.low_rung_success_rate += (
            obj_team["low_rung_successes"] / obj_team["matches_played"]
        )
        predicted_values.mid_rung_success_rate += (
            obj_team["mid_rung_successes"] / obj_team["matches_played"]
        )
        predicted_values.high_rung_success_rate += (
            obj_team["high_rung_successes"] / obj_team["matches_played"]
        )
        predicted_values.traversal_rung_success_rate += (
            obj_team["traversal_rung_successes"] / obj_team["matches_played"]
        )

    def calculate_predicted_balls_score(self, predicted_values, obj_team):
        """Calculates the predicted score from balls.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        obj_team is a list of dictionaries of objective team data.
        tba_team is a list of dictionaries of tba team data.
        The value of [stage]_balls_percent_inner is a decimal between 1 and 0."""
        # Find the predicted balls scored in auto
        predicted_values.auto_low_balls += obj_team["auto_avg_low_balls"]
        predicted_values.auto_high_balls += obj_team["auto_avg_high_balls"]

        # Find the predicted balls scored in tele
        predicted_values.tele_low_balls += obj_team["tele_avg_low_balls"]
        predicted_values.tele_high_balls += obj_team["tele_avg_high_balls"]

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
                team_data
                for team_data in obj_team_data
                if team_data["team_number"] == team
            ][0]
            tba_team = [
                team_data
                for team_data in tba_team_data
                if team_data["team_number"] == team
            ][0]

            self.calculate_predicted_balls_score(predicted_values, obj_team)
            self.calculate_predicted_climb_success_rate(predicted_values, obj_team)

            # Calculates rates of success for auto line, climb, and park out of all matches played
            # Doesn't use climb_percent_success because it is calculated out of climb attempts, not matches played
            predicted_values.auto_line_success_rate += (
                tba_team["auto_line_successes"] / obj_team["matches_played"]
            )

        for data_field in dataclasses.asdict(predicted_values).keys():
            total_score += (
                getattr(predicted_values, data_field) * self.POINTS[data_field]
            )

        return total_score

    def calculate_predicted_climb_rp(self, predicted_values):
        """Calculates whether an alliance is expected to earn the endgame RP.

        predicted_values is a dataclass which stores the predicted number of balls scored and success rates.
        """
        endgame_score = 0
        endgame_score += (
            predicted_values.low_rung_success_rate
            * self.POINTS["low_rung_success_rate"]
            + predicted_values.mid_rung_success_rate
            * self.POINTS["mid_rung_success_rate"]
            + predicted_values.high_rung_success_rate
            * self.POINTS["high_rung_success_rate"]
            + predicted_values.traversal_rung_success_rate
            * self.POINTS["traversal_rung_success_rate"]
        )

        if endgame_score >= self.ENDGAME_CLIMB_THRESHOLD:
            return 1.0
        return 0.0

    def calculate_predicted_ball_rp(self, obj_team, predicted_values):
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

    def get_final_values(self, aim, tba_match_data):
        """Finds whether or not the predicted match was played to store the final values."""
        final_predictions = {
            "final_predicted_score": 0.0,
            "final_predicted_rp1": 0.0,
            "final_predicted_rp2": 0.0,
            "has_final_scores": False,
        }
        alliance_color_is_red = aim["alliance_color"] == "R"
        aim_data = self.server.db.find(
            "predicted_aim",
            match_number=aim["match_number"],
            alliance_color_is_red=alliance_color_is_red,
        )
        if aim_data != []:
            current_predicted_aim = aim_data[0]
            # If the aim already has final predictions, return a blank dictionary so nothing is changed
            if current_predicted_aim["has_final_scores"]:
                return {}
            # Checks the value of winning_alliance to determine if the match has been played.
            # If there is no data for the match, winning_alliance is an empty string.
            for match in tba_match_data:
                if (
                    match["match_number"] == aim["match_number"]
                    and match["post_result_time"] != None
                ):
                    final_predictions = {}
                    final_predictions["final_predicted_score"] = current_predicted_aim[
                        "predicted_score"
                    ]
                    final_predictions["final_predicted_rp1"] = current_predicted_aim[
                        "predicted_rp1"
                    ]
                    final_predictions["final_predicted_rp2"] = current_predicted_aim[
                        "predicted_rp2"
                    ]
                    final_predictions["has_final_scores"] = True
                    break
        return final_predictions

    def get_actual_values(self, aim, tba_match_data):
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
                and match["post_result_time"] != None
            ):
                actual_aim = match["score_breakdown"]
                if aim["alliance_color"] == "R":
                    alliance_color = "red"
                else:
                    alliance_color = "blue"
                actual_match_dict["actual_score"] = actual_aim[alliance_color][
                    "totalPoints"
                ]
                # TBA stores RPs as booleans. If the RP is true, they get 1 RP, otherwise they get 0.
                if actual_aim[alliance_color]["cargoBonusRankingPoint"]:
                    actual_match_dict["actual_rp1"] = 1.0
                if actual_aim[alliance_color]["hangarBonusRankingPoint"]:
                    actual_match_dict["actual_rp2"] = 1.0
                # Gets whether the alliance won the match by checking the winning alliance against the alliance color/
                actual_match_dict["won_match"] = (
                    match["winning_alliance"] == alliance_color
                )
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
        tba_match_data = tba_communicator.tba_request(
            f"event/{self.server.TBA_EVENT_KEY}/matches"
        )

        filtered_aims_list = self.filter_aims_list(obj_team, tba_team, aims_list)

        for aim in filtered_aims_list:
            predicted_values = PredictedAimScores()
            update = {
                "match_number": aim["match_number"],
                "alliance_color_is_red": aim["alliance_color"] == "R",
            }
            update.update(self.get_final_values(aim, tba_match_data))
            update["predicted_score"] = self.calculate_predicted_alliance_score(
                predicted_values, obj_team, tba_team, aim["team_list"]
            )
            update["predicted_rp1"] = self.calculate_predicted_ball_rp(
                obj_team, predicted_values
            )
            update["predicted_rp2"] = self.calculate_predicted_climb_rp(
                predicted_values
            )
            update.update(self.get_actual_values(aim, tba_match_data))
            updates.append(update)
        return updates

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
