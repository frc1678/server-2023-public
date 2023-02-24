from datetime import datetime

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import utils
import logging

log = logging.getLogger(__name__)


class SimPrecisionCalc(BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_totals"]
        self.sim_schema = utils.read_schema("schema/calc_sim_precision_schema.yml")

    def get_tba_aim_score(self, match_number, alliance_color_is_red, tba_match_data):
        """Gets the total grid score for an alliance in match from TBA.
        aim is a dictionary with a match number and alliance color.
        tba_match_data is the result of a TBA request for matches.
        """
        if alliance_color_is_red:
            alliance_color = "red"
        else:
            alliance_color = "blue"
        for match in tba_match_data:
            if (
                match["match_number"] == match_number
                and match["comp_level"] == "qm"
                and match["score_breakdown"] != None
            ):
                # only use the grid score from the gamepieces to check the accuracy of scouts
                score = match["score_breakdown"][alliance_color]["autoGamePiecePoints"]
                score += match["score_breakdown"][alliance_color]["teleopGamePiecePoints"]
                # gets all the auto nodes that are empty, if there are none, it returns None (used for adjusting auto intakes from nodes)
                tba_grids = self.get_empty_auto_nodes(match["score_breakdown"][alliance_color])
                return score, tba_grids
        return None, {}

    def get_empty_auto_nodes(self, score_breakdown):
        """Returns the number of empty auto nodes in each row"""
        # Get grids in auto and teleop
        autoCommunity = score_breakdown["autoCommunity"]
        teleopCommunity = score_breakdown["teleopCommunity"]

        # Dictionary to translate rows to intakes for comparisons in get_adjusted_tba_score()
        rows_to_intakes = {"B": "intakes_low_row", "M": "intakes_mid_row", "T": "intkes_high_row"}

        empty_nodes = {}
        for row in autoCommunity:
            for index, piece in enumerate(autoCommunity[row]):
                # Check for if there is a piece in the autoCommunity grid that is empty in the teleopCommunity grid
                if piece != "None":
                    if teleopCommunity[row][index] == "None":
                        empty_nodes[rows_to_intakes[row]] = (
                            empty_nodes.get(rows_to_intakes[row], 0) + 1
                        )
        return empty_nodes

    def get_scout_tim_score(self, scout, match_number, required):
        """Gets the score for a team in a match reported by a scout.
        required is the dictionary of required datapoints: point values from schema
        """
        scout_data = self.server.db.find(
            "unconsolidated_totals", {"match_number": match_number, "scout_name": scout}
        )

        if scout_data == []:
            log.warning(f"No data from Scout {scout} in Match {match_number}")
            return

        scout_document = scout_data[0]
        total_score = 0
        for datapoint, point_value in required.items():
            # split using . to get rid of collection name
            datapoint = datapoint.split(".")[1]
            total_score += scout_document[datapoint] * point_value
        return total_score

    def get_scout_intake_row(self, scout, match_number, intakes):
        """Gets the intakes from the row for each scout.
        intakes is each intake field that is collected"""
        scout_data = self.server.db.find(
            "unconsolidated_totals", {"match_number": match_number, "scout_name": scout}
        )
        if scout_data == []:
            log.warning(f"No data from Scout {scout} in Match {match_number}")
            return
        scout_document = scout_data[0]
        total_intakes = {}
        for intake in intakes:
            # split using . to get rid of collection name
            intake = intake.split(".")[1]
            total_intakes[intake] = scout_document[intake]
        return total_intakes

    def get_aim_scout_scores(self, match_number, alliance_color_is_red, required, intakes):
        """Gets the individual TIM scores reported by each scout for an alliance in a match.
        required is the dictionary of required datapoints: point values from schema.
        Returns a dictionary where keys are team numbers and values are dictionaries of scout name: tim score.
        """
        scores_per_team = {}
        intakes_per_team = {}
        scout_data = self.server.db.find(
            "unconsolidated_totals",
            {
                "match_number": match_number,
                "alliance_color_is_red": alliance_color_is_red,
            },
        )
        teams = set([document["team_number"] for document in scout_data])
        # Populate dictionary with teams in alliance
        for team in teams:
            scores_per_team[team] = {}
            intakes_per_team[team] = {}
        for document in scout_data:
            scout_tim_score = self.get_scout_tim_score(
                document["scout_name"], match_number, required
            )
            scores_per_team[document["team_number"]].update(
                {document["scout_name"]: scout_tim_score}
            )
            scout_intakes = self.get_scout_intake_row(document["scout_name"], match_number, intakes)
            intakes_per_team[document["team_number"]].update(
                {document["scout_name"]: scout_intakes}
            )

        return scores_per_team, intakes_per_team

    def get_adjusted_tba_score(self, tba_aim_score, aim_intakes, empty_auto_nodes):
        """Using all of the intakes from the grid that each scout reports, returns the adjusted tba score.
        Uses empty auto nodes to figure out if auto points need to be added instead of teleop points."""

        # Point values of each row for teleop and auto
        tele_intake_values = {"intakes_high_row": 5, "intakes_mid_row": 3, "intakes_low_row": 2}
        auto_intake_values = {"intakes_high_row": 6, "intakes_mid_row": 4, "intakes_low_row": 3}

        # Add the number of points the scouts should be over by to tba
        for intake_type, intake_count in aim_intakes.items():
            # Check if there are any empty auto nodes in that row
            if empty_auto_nodes.get(intake_type) is not None:
                # If empty auto nodes is greater than or equal to intakes counted, just add from the auto values
                if intake_count - empty_auto_nodes[intake_type] > 0:
                    tba_aim_score += tele_intake_values[intake_type] * (
                        intake_count - empty_auto_nodes[intake_type]
                    )
                tba_aim_score += auto_intake_values[intake_type] * (empty_auto_nodes[intake_type])
            else:
                tba_aim_score += tele_intake_values[intake_type] * intake_count

        return tba_aim_score

    def get_aim_scout_avg_errors(
        self,
        aim_scout_scores,
        tba_aim_score,
        match_number,
        alliance_color_is_red,
        aim_scout_intakes,
        empty_auto_nodes,
    ):
        """Gets the average error from TBA of each scout's linear combinations in an AIM."""
        if len(aim_scout_scores) < 3:
            log.warning(
                f"Missing scout data for Match {match_number}, Alliance is Red: {alliance_color_is_red}"
            )
            return {}

        # Get the scores and intakes for each scout
        team1_scouts, team2_scouts, team3_scouts = aim_scout_scores.values()
        intake_team1_scouts, intake_team2_scouts, intake_team3_scouts = aim_scout_intakes.values()

        all_scout_errors = {}
        for scout1, score1 in team1_scouts.items():
            aim_intakes = {}
            scout1_errors = all_scout_errors.get(scout1, [])
            aim_intakes.update(intake_team1_scouts[scout1])
            for scout2, score2 in team2_scouts.items():
                # Make a copy of the aim_intakes so that each scout2's intakes gets removed before the next scout (so intakes don't stack up)
                aim_intakes_2 = aim_intakes.copy()
                scout2_errors = all_scout_errors.get(scout2, [])
                aim_intakes.update(
                    (intake_type, aim_intakes.get(intake_type, 0) + intakes)
                    for intake_type, intakes in intake_team2_scouts[scout2].items()
                )
                for scout3, score3 in team3_scouts.items():
                    # Make a copy of the aim_intakes so that each scout3's intakes gets removed before the next scout (so intakes don't stack up)
                    aim_intakes_3 = aim_intakes.copy()
                    scout3_errors = all_scout_errors.get(scout3, [])
                    aim_intakes.update(
                        (intake_type, aim_intakes.get(intake_type, 0) + intakes)
                        for intake_type, intakes in intake_team3_scouts[scout3].items()
                    )
                    adjusted_tba_aim_score = self.get_adjusted_tba_score(
                        tba_aim_score, aim_intakes, empty_auto_nodes
                    )
                    error = adjusted_tba_aim_score - (score1 + score2 + score3)
                    scout1_errors.append(error)
                    scout2_errors.append(error)
                    scout3_errors.append(error)
                    all_scout_errors[scout3] = scout3_errors
                    # reset aim_intakes to what it was before the 3rd scout's updated intakes
                    aim_intakes = aim_intakes_3
                all_scout_errors[scout2] = scout2_errors
                # reset aim_intakes to what it was before the 2nd scout's updated intakes
                aim_intakes = aim_intakes_2
            all_scout_errors[scout1] = scout1_errors
        scout_avg_errors = {scout: self.avg(errors) for scout, errors in all_scout_errors.items()}
        return scout_avg_errors

    def calc_sim_precision(self, sim, tba_match_data):
        """Calculates the average difference between errors where the scout was part of the combination, and errors where the scout wasn't.
        sim is a scout-in-match document."""
        calculations = {}
        tba_aim_score, empty_auto_nodes = self.get_tba_aim_score(
            sim["match_number"], sim["alliance_color_is_red"], tba_match_data
        )
        for calculation, schema in self.sim_schema["calculations"].items():
            required = schema["requires"]
            intakes = schema["intakes"]
            # Score reported by a specific scout for a robot in a match
            scout_tim_score = self.get_scout_tim_score(
                sim["scout_name"], sim["match_number"], required
            )
            # Get the average errors of all scouts in a match
            aim_scout_scores, aim_scout_intakes = self.get_aim_scout_scores(
                sim["match_number"], sim["alliance_color_is_red"], required, intakes
            )
            aim_scout_errors = self.get_aim_scout_avg_errors(
                aim_scout_scores,
                tba_aim_score,
                sim["match_number"],
                sim["alliance_color_is_red"],
                aim_scout_intakes,
                empty_auto_nodes,
            )
            if aim_scout_errors == {}:
                continue

            aim_intakes = {}
            # Find the scout's, whose sim precision we are calculating, number of intakes from grid
            aim_intakes.update(aim_scout_intakes[sim["team_number"]][sim["scout_name"]])

            # Remove the team scouted by the scout, only consider alliance partners
            aim_scout_scores.pop(sim["team_number"])
            aim_scout_intakes.pop(sim["team_number"])

            ally1_scouts = list(aim_scout_scores.values())[0]
            ally2_scouts = list(aim_scout_scores.values())[1]
            intake1_scouts = list(aim_scout_intakes.values())[0]
            intake2_scouts = list(aim_scout_intakes.values())[1]

            # Calculate the sim precision using the avg errors of the scout vs the avg error of each scout
            sim_errors = []
            for scout1, ally1_score in ally1_scouts.items():
                aim_intakes_1 = aim_intakes.copy()
                aim_intakes.update(
                    (intake_type, aim_intakes.get(intake_type, 0) + intakes)
                    for intake_type, intakes in intake1_scouts[scout1].items()
                )
                for scout2, ally2_score in ally2_scouts.items():
                    aim_intakes_2 = aim_intakes.copy()
                    aim_intakes.update(
                        (intake_type, aim_intakes.get(intake_type, 0) + intakes)
                        for intake_type, intakes in intake2_scouts[scout2].items()
                    )
                    current_combo_error = self.get_adjusted_tba_score(
                        tba_aim_score, aim_intakes, empty_auto_nodes
                    ) - (scout_tim_score + ally1_score + ally2_score)
                    # Each aim_scout_error value represents the average error of 3 scouts, so divide by 3
                    average_partner_error = (
                        aim_scout_errors[scout1] + aim_scout_errors[scout2]
                    ) / 3
                    error_difference = average_partner_error - current_combo_error
                    sim_errors.append(error_difference)
                    aim_intakes = aim_intakes_2
                aim_intakes = aim_intakes_1
            calculations[calculation] = self.avg(sim_errors)
        return calculations

    def update_sim_precision_calcs(self, unconsolidated_sims):
        """Creates scout-in-match precision updates"""
        tba_match_data = tba_communicator.tba_request(f"event/{utils.TBA_EVENT_KEY}/matches")
        updates = []
        for sim in unconsolidated_sims:
            sim_data = self.server.db.find("unconsolidated_totals", sim)[0]
            update = {}
            update["scout_name"] = sim_data["scout_name"]
            update["match_number"] = sim_data["match_number"]
            update["team_number"] = sim_data["team_number"]
            for match in tba_match_data:
                if (
                    match["match_number"] == sim_data["match_number"]
                    and match["comp_level"] == "qm"
                ):
                    # Convert match timestamp from Unix time (on TBA) to human readable
                    update["timestamp"] = datetime.fromtimestamp(match["actual_time"])
                    break
            if (sim_precision := self.calc_sim_precision(sim_data, tba_match_data)) != {}:
                update.update(sim_precision)
            updates.append(update)
        return updates

    def run(self):
        entries = self.entries_since_last()
        sims = []
        for entry in entries:
            sims.append(
                {
                    "scout_name": entry["o"]["scout_name"],
                    "match_number": entry["o"]["match_number"],
                }
            )
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("sim_precision")

        for update in self.update_sim_precision_calcs(sims):
            self.server.db.update_document(
                "sim_precision",
                update,
                {
                    "scout_name": update["scout_name"],
                    "match_number": update["match_number"],
                },
            )
