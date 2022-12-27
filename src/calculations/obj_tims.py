#!/usr/bin/env python3
# Copyright (c) 2022 FRC Team 1678: Citrus Circuits
"""Defines class methods to consolidate and calculate Team In Match (TIM) data."""

import copy
import statistics
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict


class ObjTIMCalcs(BaseCalculations):
    schema = utils.read_schema("schema/calc_obj_tim_schema.yml")
    type_check_dict = {"float": float, "int": int, "str": str, "bool": bool}

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_obj_tim"]

    def consolidate_nums(self, nums: List[Union[int, float]]) -> int:
        """Given numbers reported by multiple scouts, estimates actual number
        nums is a list of numbers, representing action counts or times, reported by each scout
        Currently tries to consolidate using only the reports from scouts on one robot,
        but future improvements might change the algorithm to account for other alliance members,
        since TBA can give us the total action counts for the alliance
        """
        mean = self.avg(nums)
        if len(nums) == 0 or mean in nums:
            # Avoid getting a divide by zero error when calculating standard deviation
            return round(mean)
        # If two or more scouts agree, automatically go with what they say
        if len(nums) > len(set(nums)):
            # Still need to consolidate, in case there are multiple modes
            return self.consolidate_nums(self.modes(nums))
        # Population standard deviation:
        std_dev = statistics.pstdev(nums)
        # Calculate weighted average, where the weight for each num is its reciprocal square z-score
        # That way, we account less for data farther from the mean
        z_scores = [(num - mean) / std_dev for num in nums]
        weights = [1 / z**2 for z in z_scores]
        float_nums = self.avg(nums, weights)
        return round(float_nums)

    def consolidate_bools(self, bools: list) -> bool:
        """Given a list of booleans reported by multiple scouts, returns the actual value"""
        bools = self.modes(bools)
        if len(bools) == 1:
            # Go with the majority
            return bools[0]
        # Scouts are evenly split, so just go with False
        return False

    def consolidate_categorical_actions(self, unconsolidated_tims: List[Dict]):
        """Given string type obj_tims, return actual string"""
        # Dictionary for final calculated tims
        final_categorical_actions = {}
        # Dictionary for associated category actions
        categories = {
            "climb_level": ["NONE", "LOW", "MID", "HIGH", "TRAVERSAL"],
            "start_position": ["ONE", "TWO", "THREE", "FOUR"],
        }
        for category in self.schema["categorical_actions"]:
            categorical_actions = [scout[category] for scout in unconsolidated_tims]
            # If at least 2 scouts agree, take their answer
            if len(self.modes(categorical_actions)) == 1:
                final_categorical_actions[category] = self.modes(categorical_actions)[0]
                continue

            # Add up the indexes of the scout responses
            category_avg = self.avg(
                [categories[category].index(value) for value in categorical_actions]
            )
            # Round the average and append the correct action to the final dict
            final_categorical_actions[category] = categories[category][round(category_avg)]
        return final_categorical_actions

    def filter_timeline_actions(self, tim: dict, **filters) -> list:
        """Removes timeline actions that don't meet the filters and returns all the actions that do"""
        actions = tim["timeline"]
        for field, required_value in filters.items():
            if tim["climb_level"] != "NONE" and required_value == "climb_attempt":
                # Counting climbs based on attempts sometimes yields an over 100% climb success
                actions = [{"time": 149, "action_type": "climb_attempt"}]
                break
            elif field == "time":
                # Times are given as closed intervals: either [0,134] or [135,150]
                actions = filter(
                    lambda action: required_value[0] <= action["time"] <= required_value[1], actions
                )
            else:
                # Removes actions for which action[field] != required_value
                actions = filter(lambda action: action[field] == required_value, actions)
            # filter returns an iterable object
            actions = list(actions)
        return actions

    def count_timeline_actions(self, tim: dict, **filters) -> int:
        """Returns the number of actions in one TIM timeline that meets the required filters"""
        return len(self.filter_timeline_actions(tim, **filters))

    def total_time_between_actions(
        self, tim: dict, start_action: str, end_action: str, min_time: int
    ) -> int:
        """Returns total number of seconds spent between two types of actions for a given TIM

        start_action and end_action are the names (types) of those two actions,
        such as start_incap and end_climb.
        min_time is the minimum number of seconds between the two types of actions that we want to count
        """
        start_actions = self.filter_timeline_actions(tim, action_type=start_action)
        end_actions = self.filter_timeline_actions(tim, action_type=end_action)
        # Match scout app should automatically add an end action at the end of the match,
        # if there isn't already an end action after the last start action. That way there are the
        # same number of start actions and end actions.
        total_time = 0
        for start, end in zip(start_actions, end_actions):
            if start["time"] - end["time"] >= min_time:
                total_time += start["time"] - end["time"]
        return total_time

    def calculate_tim_counts(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated count based data fields"""
        calculated_tim = {}
        for calculation, filters in self.schema["timeline_counts"].items():
            unconsolidated_counts = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(filters)
            expected_type = filters_.pop("type")
            for tim in unconsolidated_tims:
                new_count = self.count_timeline_actions(tim, **filters_)
                if not isinstance(new_count, self.type_check_dict[expected_type]):
                    raise TypeError(f"Expected {new_count} calculation to be a {expected_type}")
                unconsolidated_counts.append(new_count)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_counts)
        return calculated_tim

    def calculate_tim_times(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns the calculated time data fields"""
        calculated_tim = {}
        for calculation, action_types in self.schema["timeline_cycle_time"].items():
            unconsolidated_cycle_times = []
            # Variable type of a calculation is in the schema, but it's not a filter
            filters_ = copy.deepcopy(action_types)
            expected_type = filters_.pop("type")
            for tim in unconsolidated_tims:
                # action_types is a list of dictionaries, where each dictionary is
                # "action_type" to the name of either the start or end action
                new_cycle_time = self.total_time_between_actions(
                    tim,
                    action_types["start_action"],
                    action_types["end_action"],
                    action_types["minimum_time"],
                )
                if not isinstance(new_cycle_time, self.type_check_dict[expected_type]):
                    raise TypeError(
                        f"Expected {new_cycle_time} calculation to be a {expected_type}"
                    )
                unconsolidated_cycle_times.append(new_cycle_time)
            calculated_tim[calculation] = self.consolidate_nums(unconsolidated_cycle_times)
        return calculated_tim

    def calculate_unconsolidated_tims(self, unconsolidated_tims: List[Dict]):
        """Given a list of unconsolidated TIMS, returns the unconsolidated calculated TIMs"""
        if len(unconsolidated_tims) == 0:
            utils.log_warning("calculate_tim: zero TIMs given")
            return {}

        unconsolidated_totals = []
        # Calculates unconsolidated tim counts
        for tim in unconsolidated_tims:
            tim_totals = {}
            tim_totals["scout_name"] = tim["scout_name"]
            tim_totals["match_number"] = tim["match_number"]
            tim_totals["team_number"] = tim["team_number"]
            tim_totals["alliance_color_is_red"] = tim["alliance_color_is_red"]
            # Calculate unconsolidated tim counts
            for aggregate, filters in self.schema["aggregates"].items():
                total_count = 0
                aggregate_counts = filters["counts"]
                for calculation, filters in self.schema["timeline_counts"].items():
                    filters_ = copy.deepcopy(filters)
                    expected_type = filters_.pop("type")
                    new_count = self.count_timeline_actions(tim, **filters_)
                    if not isinstance(new_count, self.type_check_dict[expected_type]):
                        raise TypeError(f"Expected {new_count} calculation to be a {expected_type}")
                    tim_totals[calculation] = new_count
                    # Calculate unconsolidated aggregates
                    for count in aggregate_counts:
                        if calculation == count:
                            total_count += new_count
                    tim_totals[aggregate] = total_count
            # Calculate unconsolidated categorical actions
            for category in self.schema["categorical_actions"]:
                tim_totals[category] = tim[category]
            unconsolidated_totals.append(tim_totals)
        return unconsolidated_totals

    def calculate_aggregates(self, calculated_tim: List[Dict]):
        """Given a list of consolidated tims by calculate_tim_counts, return consolidated aggregates"""
        final_aggregates = {}
        # Get each aggregate and its associated counts
        for aggregate, filters in self.schema["aggregates"].items():
            total_count = 0
            aggregate_counts = filters["counts"]
            # Add up all the counts for each aggregate and add them to the final dictionary
            for count in aggregate_counts:
                total_count += calculated_tim[count]
                final_aggregates[aggregate] = total_count
        return final_aggregates

    def calculate_tim(self, unconsolidated_tims: List[Dict]) -> dict:
        """Given a list of unconsolidated TIMs, returns a calculated TIM"""
        if len(unconsolidated_tims) == 0:
            utils.log_warning("calculate_tim: zero TIMs given")
            return {}
        calculated_tim = {}
        calculated_tim.update(self.calculate_tim_counts(unconsolidated_tims))
        calculated_tim.update(self.calculate_tim_times(unconsolidated_tims))
        calculated_tim.update(self.consolidate_categorical_actions(unconsolidated_tims))
        calculated_tim.update(self.calculate_aggregates(calculated_tim))
        # Use any of the unconsolidated TIMs to get the team and match number,
        # since that should be the same for each unconsolidated TIM
        calculated_tim["match_number"] = unconsolidated_tims[0]["match_number"]
        calculated_tim["team_number"] = unconsolidated_tims[0]["team_number"]
        # confidence_rating is the number of scouts that scouted one robot
        calculated_tim["confidence_ranking"] = len(unconsolidated_tims)
        return calculated_tim

    def update_calcs(self, tims: List[Dict[str, Union[str, int]]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': '1678', 'match_number': 69}"""
        calculated_tims = []
        unconsolidated_totals = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            calculated_tims.append(self.calculate_tim(unconsolidated_obj_tims))
            unconsolidated_totals.extend(
                self.calculate_unconsolidated_tims(unconsolidated_obj_tims)
            )
        return calculated_tims, unconsolidated_totals

    def run(self):
        """Executes the OBJ TIM calculations"""
        # Get oplog entries
        tims = []
        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    utils.log_warning(f"obj_tims: team number {team_num} is not in teams list")
                tims.append(
                    {
                        "team_number": team_num,
                        "match_number": entry["o"]["match_number"],
                    }
                )
        unique_tims = []
        for tim in tims:
            if tim not in unique_tims:
                unique_tims.append(tim)
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("obj_tim")

        updates = self.update_calcs(unique_tims)
        for update in updates[0]:
            if update != {}:
                self.server.db.update_document(
                    "obj_tim",
                    update,
                    {"team_number": update["team_number"], "match_number": update["match_number"]},
                )
        if len(updates) > 1:
            for document in updates[1]:
                self.server.db.update_document(
                    "unconsolidated_totals",
                    document,
                    {
                        "team_number": document["team_number"],
                        "match_number": document["match_number"],
                        "scout_name": document["scout_name"],
                    },
                )
