#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Holds functions used to determine auto scoring and paths"""

from typing import List, Dict
from calculations.base_calculations import BaseCalculations
import logging
import statistics
import utils
import random  # ONLY NEEDED UNTIL SPR IS IMPLEMENTED

log = logging.getLogger(__name__)


class AutoPathCalc(BaseCalculations):
    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_obj_tim"]

    def get_unconsolidated_auto_timelines(
        self, unconsolidated_obj_tims: List[Dict]
    ) -> List[List[Dict]]:
        "Given unconsolidated_obj_tims, returns unconsolidated auto timelines"

        unconsolidated_auto_timelines = []

        # Extract auto timelines
        for unconsolidated_tim in unconsolidated_obj_tims:
            unconsolidated_auto_timelines.append(
                [
                    action
                    for action in unconsolidated_tim["timeline"]
                    if action["in_teleop"] == False
                ]
            )
        return unconsolidated_auto_timelines

    def consolidate_timelines(self, unconsolidated_timelines: List[List[Dict]]) -> List[Dict]:
        "Given a list of unconsolidated auto timelines (output from the get_unconsolidated_auto_timelines function), consolidates the timelines into a single timeline."

        ut = unconsolidated_timelines  # alias
        consolidated_timeline = []

        # If all three timelines are empty, return empty list
        if (max_length := max([len(timeline) for timeline in ut])) == 0:
            return consolidated_timeline

        # Iterate through the longest timeline
        for i in range(max_length):
            # values is a list to store the value of every item in the action dict
            # {"in_teleop": False, "time": 140, "action_type": "score_cone_high"}
            # Should look something like [False, False, False], [139, 140, 138], or ["score_cone_high", "score_cube_mid", "score_cone_high"]
            values = []

            # Get all variables in the action dict
            for name in list(filter(lambda x: len(x) == max_length, ut))[0][0].keys():
                # For every unconsolidated timeline, take the value of the variable in the current action dict
                for j in range(len(ut)):
                    # If the action at index i exists in the timeline, append the value of the variable
                    try:
                        values.append(ut[j][i][name])
                    # If not, append None
                    except:
                        values.append(None)

                # Check if there is a mode
                if len(mode := BaseCalculations.modes(values)) == 1:
                    # If the mode is None (meaning that most or all timelines don't have an action at that index), don't add it to the consolidated timeline
                    if mode == [None]:
                        # Reset values list
                        values = []
                        continue

                    # If an action of that index already exists, add the mode to it
                    try:
                        consolidated_timeline[i][name] = mode[0]
                    # If not, create a new action at that index
                    except:
                        consolidated_timeline.append({name: mode[0]})

                # If values are integers, take average and round it
                elif len(list(filter(lambda y: type(y) is not int, values))) == 0:
                    # If an action of that index already exists, add the average to it
                    try:
                        consolidated_timeline[i][name] = round(statistics.mean(values))
                    # If not, create a new action at that index
                    except IndexError:
                        consolidated_timeline.append({name: round(statistics.mean(values))})

                else:
                    # PLACEHOLDER UNTIL SPR IS IMPLEMENTED
                    # CURRENTLY CHOOSES A RANDOM VALUE
                    # WHEN SPR IS IMPLEMENTED, WILL CHOOSE THE ACTION FROM THE MOST PRECISE SCOUT
                    # If an action of that index already exists, add the value to it
                    try:
                        consolidated_timeline[i][name] = random.choice(values)
                    # If not, create a new action at that index
                    except:
                        consolidated_timeline.append({name: random.choice(values)})

                # Reset values list
                values = []

        return consolidated_timeline

    def get_consolidated_auto_variables(self, calculated_tim: Dict) -> Dict:
        "Given a calculated_tim, return auto variables start_position, preloaded_gamepiece, and auto_charge_level"
        # Auto variables we collect
        auto_variables = ["start_position", "preloaded_gamepiece", "auto_charge_level"]

        tim_auto_values = {}
        for variable in auto_variables:
            tim_auto_values[variable] = calculated_tim[variable]
        # Create match_numbers, because auto path documents have multiple match numbers now
        tim_auto_values["match_numbers"] = [calculated_tim["match_number"]]

        return tim_auto_values

    def create_auto_fields(self, tim, subj_tim: Dict) -> Dict:
        """Creates auto fields for one tim such as score_1, intake_1, etc using the consolidated_timeline"""
        # TODO: USE A SCHEMA FOR THIS FUNCTION (very hardcoded rn ur welcome)
        # counters to cycle through scores and intakes
        intake_count = 1
        score_count = 1
        # Use subj_tim to figure out which pieces are in which auto position
        if subj_tim != {}:
            num_enum = {"one": 1, "two": 2, "three": 3, "four": 4}
            piece_enum = {0: "cone", 1: "cube", 2: "none"}
            auto_pieces_start_position = [
                piece_enum[piece] for piece in subj_tim["auto_pieces_start_position"]
            ]
        # set scores and intakes to None (in order to not break exports)
        update = {
            "score_1_piece": None,
            "score_1_position": None,
            "score_2_piece": None,
            "score_2_position": None,
            "intake_1_piece": None,
            "intake_1_position": None,
            "intake_2_piece": None,
            "intake_2_position": None,
            "score_3_piece": None,
            "score_3_position": None,
        }

        # Look up if they got mobiility in tba_tims and add it as a variable
        update["mobility"] = self.server.db.find(
            "tba_tim", {"match_number": tim["match_number"], "team_number": tim["team_number"]}
        )[0]["mobility"]

        # For each action in the consolidated timeline, add it to one of the new fields (if it applies)
        for action in tim["auto_timeline"]:
            # BUG: action_type can sometimes be null, need better tests in auto_paths, more edge cases
            if action["action_type"] is None:
                log.warning("auto_paths: action_type is null")
                continue
            if "score" in action["action_type"]:
                # split action type to only include piece and position (example: "score_cone_high" to just "cone_high")
                if "fail" not in action["action_type"]:
                    update[f"score_{score_count}_piece"] = action["action_type"].split("_")[1]
                    update[f"score_{score_count}_position"] = action["action_type"].split("_")[2]
                else:
                    update[f"score_{score_count}_piece"] = "fail"
                    update[f"score_{score_count}_position"] = "fail"
                score_count += 1
            elif "intake" in action["action_type"]:
                # split action type to only include position (example: "auto_intake_four" to just "four")
                if subj_tim != {}:
                    update[f"intake_{intake_count}_piece"] = auto_pieces_start_position[
                        num_enum[action["action_type"].split("_")[-1]] - 1
                    ]
                update[f"intake_{intake_count}_position"] = action["action_type"].split("_")[-1]
                intake_count += 1
        return update

    def group_auto_paths(self, tim, calculated_tims):
        """Compares auto path with other auto paths at the same start position"""
        # Find all current auto paths with this team number and start position
        current_documents = self.server.db.find(
            "auto_paths",
            {"team_number": tim["team_number"], "start_position": tim["start_position"]},
        )
        # Add the current calculated_tims into current documents (because these tims aren't in server yet)
        current_documents.extend(
            [
                calculated_tim
                for calculated_tim in calculated_tims
                if (
                    calculated_tim["team_number"] == tim["team_number"]
                    and calculated_tim["start_position"] == tim["start_position"]
                )
            ]
        )
        # List of all charge levels that can be put in the same auto path (because all are attempting to engage in auto)
        charge_levels = ["F", "D", "E"]
        # List of all scoring positions (fail and None are in here to not break the indexing)
        scoring_rows = [None, "fail", "low", "mid", "high"]

        # If current_documents is empty, that means this is the first auto path at this start position
        if not current_documents:
            tim["matches_ran"] = 1
            tim["path_number"] = 1
            # Sets to 0 or 1 depending on if it engages or not
            tim["auto_charge_successes"] = int(tim["auto_charge_level"] == "E")
            for i in range(1, 4):
                tim[f"score_{i}_piece_successes"] = int(
                    tim[f"score_{i}_piece"] != "fail" and tim[f"score_{i}_piece"] is not None
                )
                # The highest scoring position's successes is equal to the successes bc this is the first match ran
                tim[f"score_{i}_max_piece_successes"] = tim[f"score_{i}_piece_successes"]
        else:
            for document in current_documents:
                # Checks to see if intake fields match, then we can compare the rest manually
                if all(
                    tim[field] == value
                    for field, value in document.items()
                    if field
                    in ["intake_1_position", "intake_2_position", "mobility", "preloaded_gamepiece"]
                ):
                    # Make a copy, in case later down the if statements the auto paths do not match
                    old_tim = tim.copy()
                    # Checks to see if both documents have an attempt at charging (not "N")
                    if (
                        document["auto_charge_level"] in charge_levels
                        and tim["auto_charge_level"] in charge_levels
                    ):
                        # Add to auto_charge_successes here because it could get overriden in the next line
                        tim["auto_charge_successes"] = document["auto_charge_successes"] + int(
                            tim["auto_charge_level"] == "E"
                        )
                        # Display the highest auto charge level for this path
                        tim["auto_charge_level"] = max(
                            document["auto_charge_level"],
                            tim["auto_charge_level"],
                            key=charge_levels.index,
                        )
                    # If one is "N", and the other is not "N", this means they are different auto paths because one attempted to charge
                    # and the other did not
                    elif document["auto_charge_level"] != tim["auto_charge_level"]:
                        continue
                    # Reset variable in order to continue the loop if this loop is broken out of
                    reset = False
                    # Use loop with numbers from 1-3 in order to iterate through scores and positions
                    for i in range(1, 4):
                        # If the scored pieces do not match but one of them is a fail, then the path is the same (but the piece wasn't scored)
                        if tim[f"score_{i}_piece"] != document[f"score_{i}_piece"] and not (
                            tim[f"score_{i}_piece"] == "fail"
                            or document[f"score_{i}_piece"] == "fail"
                        ):
                            reset = True
                            break
                        if tim[f"score_{i}_piece"] == "fail" or tim[f"score_{i}_piece"] is None:
                            # Save document data, so that the current path does not override it
                            tim[f"score_{i}_piece"] = document[f"score_{i}_piece"]
                            tim[f"score_{i}_position"] = document[f"score_{i}_position"]
                            tim[f"score_{i}_piece_successes"] = document[
                                f"score_{i}_piece_successes"
                            ]
                            tim[f"score_{i}_max_piece_successes"] = document[
                                f"score_{i}_max_piece_successes"
                            ]
                            # Continue here, because if the current path has a failed score, then successes does not need to be updated
                            continue
                        tim[f"score_{i}_piece_successes"] = (
                            document[f"score_{i}_piece_successes"] + 1
                        )
                        # If the positions are equal, that means the max was scored again (because the document always contains the max)
                        if tim[f"score_{i}_position"] == document[f"score_{i}_position"]:
                            tim[f"score_{i}_max_piece_successes"] = (
                                document[f"score_{i}_max_piece_successes"] + 1
                            )
                        # If the current path has a higher scoring position, change the max successes and the position
                        elif scoring_rows.index(
                            document[f"score_{i}_position"]
                        ) < scoring_rows.index(tim[f"score_{i}_position"]):
                            tim[f"score_{i}_max_piece_successes"] = 1
                        # This is run when the current path did not score in the maximum row seen
                        else:
                            tim[f"score_{i}_max_piece_successes"] = document[
                                f"score_{i}_max_piece_successes"
                            ]
                            # Make sure that the curent max doesn't get overriden
                            tim[f"score_{i}_position"] = document[f"score_{i}_position"]
                    # Use reset variable to reset any changes made to the tim, and continue the loop because the paths do not match
                    if reset:
                        tim = old_tim
                        continue
                    # Because of a lack of subjective data sometimes (usually on the 2nd day), sometimes we do not know the piece
                    # that was picked up, but it could still be the same auto path, so we must ignore checking it
                    # This code is just to make sure that we don't override the piece to null when it is the same auto path
                    if tim["intake_1_piece"] is None:
                        tim["intake_1_piece"] = document["intake_1_piece"]
                    if tim["intake_2_piece"] is None:
                        tim["intake_2_piece"] = document["intake_2_piece"]

                    tim["matches_ran"] = document["matches_ran"] + 1
                    tim["match_numbers"].extend(document["match_numbers"])
                    tim["path_number"] = document["path_number"]
                    break
            else:
                # If there are no matching documents, that means this is a new auto path at the same start position
                tim["matches_ran"] = 1
                tim["path_number"] = len(current_documents) + 1
                tim["auto_charge_successes"] = int(tim["auto_charge_level"] == "E")
                for i in range(1, 4):
                    tim[f"score_{i}_piece_successes"] = int(
                        tim[f"score_{i}_piece"] != "fail" and tim[f"score_{i}_piece"] is not None
                    )
                    # The highest scoring position's successes is equal to the successes bc this is the first match ran
                    tim[f"score_{i}_max_piece_successes"] = tim[f"score_{i}_piece_successes"]
        return tim

    def calculate_auto_paths(self, tims: List[Dict]) -> List[Dict]:
        """Calculates auto data for the given tims, which looks like
        [{"team_number": 1678, "match_number": 42}, {"team_number": 1706, "match_number": 56}, ...]"""
        calculated_tims = []
        for tim in tims:
            # Get data for the tim from MongoDB
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            obj_tim = self.server.db.find("obj_tim", tim)[0]
            if (subj_tim := self.server.db.find("subj_tim", tim)) == []:
                subj_tim = {}
            else:
                subj_tim = subj_tim[0]

            # Run calculations on the team in match
            tim.update(self.get_consolidated_auto_variables(obj_tim))
            tim.update(
                {
                    "auto_timeline": self.consolidate_timelines(
                        self.get_unconsolidated_auto_timelines(unconsolidated_obj_tims)
                    )
                }
            )
            tim.update(self.create_auto_fields(tim, subj_tim))
            tim.update(self.group_auto_paths(tim, calculated_tims))

            # Delete match number because it is a useless field for auto paths
            del tim["match_number"]
            # Check to see if an outdated version of the path is in calculated_tims, and remove it if it is
            for calculated_tim in calculated_tims:
                if (
                    calculated_tim["team_number"] == tim["team_number"]
                    and calculated_tim["start_position"] == tim["start_position"]
                    and calculated_tim["path_number"] == tim["path_number"]
                ):
                    calculated_tims.remove(calculated_tim)
            calculated_tims.append(tim)
        return calculated_tims

    def run(self):
        """Executes the auto_path calculations"""
        # Get oplog entries
        tims = []

        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                # Check that the entry is an unconsolidated_obj_tim
                if "timeline" not in entry["o"].keys() or "team_number" not in entry["o"].keys():
                    continue

                # Check that the team is in the team list, ignore team if not in teams list
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"auto_paths: team number {team_num} is not in teams list")
                    continue

                # Make tims list
                tims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )

        # Filter duplicate tims
        unique_tims = []
        for tim in tims:
            if tim not in unique_tims:
                unique_tims.append(tim)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("auto_paths")

        # Calculate data
        updates = self.calculate_auto_paths(unique_tims)

        # Upload data to MongoDB
        for update in updates:
            if update != {}:
                self.server.db.update_document(
                    "auto_paths",
                    update,
                    {
                        "team_number": update["team_number"],
                        "start_position": update["start_position"],
                        "path_number": update["path_number"],
                    },
                )
