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
        self.watched_collections = ["auto_paths", "unconsolidated_obj_tim", "obj_tim"]

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

        return tim_auto_values

    def create_auto_fields(self, auto_timeline: List[Dict]) -> Dict:
        """Creates auto fields such as score_1, intake_1, etc using the consolidated_timeline"""
        # TODO: USE A SCHEMA FOR THIS FUNCTION (very hardcoded rn ur welcome)
        # counters to cycle through scores and intakes
        intake_count = 1
        score_count = 1
        # set scores and intakes to None (in order to not break exports)
        update = {
            "score_1": None,
            "score_2": None,
            "intake_1": None,
            "intake_2": None,
            "score_3": None,
        }
        # For each action in the consolidated timeline, add it to one of the new fields (if it applies)
        for action in auto_timeline:
            # BUG: action_type can sometimes be null, need better tests in auto_paths, more edge cases
            if action["action_type"] is None:
                log.warning("auto_paths: action_type is null")
                continue
            if "score" in action["action_type"]:
                # split action type to only include piece and position (example: "score_cone_high" to just "cone_high")
                update[f"score_{score_count}"] = action["action_type"].split("_", 1)[1]
                score_count += 1
            elif "intake" in action["action_type"]:
                # split action type to only include position (example: "auto_intake_four" to just "four")
                update[f"intake_{intake_count}"] = action["action_type"].split("_")[-1]
                intake_count += 1
        return update

    def calculate_auto_paths(self, tims: List[Dict]) -> List[Dict]:
        """Calculates auto data for the given tims, which looks like
        [{"team_number": 1678, "match_number": 42}, {"team_number": 1706, "match_number": 56}, ...]"""
        calculated_tims = tims

        for tim in tims:
            # Get data for the tim from MongoDB
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            obj_tim = self.server.db.find("obj_tim", tim)[0]

            # Run calculations on the team in match
            calculated_tims[tims.index(tim)].update(self.get_consolidated_auto_variables(obj_tim))
            calculated_tims[tims.index(tim)].update(
                {
                    "auto_timeline": self.consolidate_timelines(
                        self.get_unconsolidated_auto_timelines(unconsolidated_obj_tims)
                    )
                }
            )
            calculated_tims[tims.index(tim)].update(
                self.create_auto_fields(calculated_tims[tims.index(tim)]["auto_timeline"])
            )
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
                        "match_number": update["match_number"],
                    },
                )
