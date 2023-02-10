# Copyright (c) 2023 FRC Team 1678: Citrus Circuits

import copy
import utils
from calculations.base_calculations import BaseCalculations
from typing import List, Union, Dict
import logging

log = logging.getLogger(__name__)


class UnconsolidatedTotals(BaseCalculations):
    schema = utils.read_schema("schema/calc_obj_tim_schema.yml")
    type_check_dict = {"float": float, "int": int, "str": str, "bool": bool}

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ["unconsolidated_obj_tim"]

    def filter_timeline_actions(self, tim: dict, **filters) -> list:
        """Removes timeline actions that don't meet the filters and returns all the actions that do"""
        actions = tim["timeline"]
        for field, required_value in filters.items():
            if field == "time":
                # Times are given as closed intervals: either [0,134] or [135,150]
                actions = filter(
                    lambda action: required_value[0] <= action["time"] <= required_value[1],
                    actions,
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

    def calculate_unconsolidated_tims(self, unconsolidated_tims: List[Dict]):
        """Given a list of unconsolidated TIMS, returns the unconsolidated calculated TIMs"""
        if len(unconsolidated_tims) == 0:
            log.warning("calculate_tim: zero TIMs given")
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

    def update_calcs(self, tims: List[Dict[str, Union[str, int]]]) -> List[dict]:
        """Calculate data for each of the given TIMs. Those TIMs are represented as dictionaries:
        {'team_number': '1678', 'match_number': 69}"""
        unconsolidated_totals = []
        for tim in tims:
            unconsolidated_obj_tims = self.server.db.find("unconsolidated_obj_tim", tim)
            unconsolidated_totals.extend(
                self.calculate_unconsolidated_tims(unconsolidated_obj_tims)
            )
        return unconsolidated_totals

    def run(self):
        """Executes the OBJ TIM calculations"""
        # Get oplog entries
        tims = []
        # Check if changes need to be made to teams
        if (entries := self.entries_since_last()) != []:
            for entry in entries:
                team_num = entry["o"]["team_number"]
                if team_num not in self.teams_list:
                    log.warning(f"obj_tims: team number {team_num} is not in teams list")
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
        if len(updates) > 1:
            for document in updates:
                self.server.db.update_document(
                    "unconsolidated_totals",
                    document,
                    {
                        "team_number": document["team_number"],
                        "match_number": document["match_number"],
                        "scout_name": document["scout_name"],
                    },
                )
