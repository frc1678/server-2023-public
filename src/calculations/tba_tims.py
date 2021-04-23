#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Run TIM calculations dependent on TBA data."""

import copy

from data_transfer import database
import utils
from src.server import Server


def calc_tba_bool(match_data, alliance, filters):
    """Returns a bool representing if match_data meets all filters defined in filters."""
    for key, value in filters.items():
        if match_data['score_breakdown'][alliance][key] != value:
            return False
    return True


def get_robot_number_and_alliance(team_num, match_data):
    """Gets the robot number (e.g. the `1` in initLineRobot1) and alliance color."""
    team_key = f'frc{team_num}'
    for alliance in ['red', 'blue']:
        for i, key in enumerate(match_data['alliances'][alliance]['team_keys'], start=1):
            if team_key == key:
                return i, alliance
    raise ValueError(f'Team {team_num} not found in match {match_data["match_number"]}')


def get_team_list_from_match(match_data):
    """Extracts list of teams that played in the match with data given in match_data."""
    teams = []
    for alliance in ['red', 'blue']:
        for team in match_data['alliances'][alliance]['team_keys']:
            teams.append(int(team[3:]))
    return teams


def update_calc_tba_tims(tims):
    """Returns a list of the TIM calcs that require TBA data to run.

    Reads from the `calc_tba_tim` schema file to get data points that are pulled from TBA.
    """
    # Pull TBA data
    tba_api_url = f'event/{Server.TBA_EVENT_KEY}/matches'
    ldc = database.Database()
    tba_data = ldc.get_tba_cache(tba_api_url)['data']
    # Filter out matches such that we only have quals matches
    # Create dictionary of match_number: match data to allow easier access
    quals_matches = {data['match_number']: data for data in tba_data if data['comp_level'] == 'qm'}
    full_tim_refs = []

    # Get team number and match number for TIMs referenced by `tims`
    # This is needed because TIMs can be passed just using match number
    for tim in tims:
        if 'team_number' in tim:
            # Ref is as specific as possible, refers to one team in one match
            if 'match_number' in tim:
                full_tim_refs.append(tim)
            else:  # Match refers to all a team's matches
                for match_num, match_data in quals_matches.items():
                    if tim['team_number'] in get_team_list_from_match(match_data):
                        full_tim_refs.append(
                            {'team_number': tim['team_number'], 'match_number': match_num}
                        )
        # Ref refers to all TIMs from a match
        elif 'match_number' in tim:
            if tim['match_number'] in quals_matches:
                for team in get_team_list_from_match(quals_matches[tim['match_number']]):
                    full_tim_refs.append({'team_number': team, 'match_number': tim['match_number']})
            else:
                utils.log_warning(f'Cannot find TBA data from q{tim["match_number"]} in cache')
        else:
            utils.log_warning(f'Invalid TBA TIM ref {tim}')

    output_data = []
    for ref in full_tim_refs:
        out = copy.deepcopy(ref)
        if quals_matches[out['match_number']]['score_breakdown'] is None:
            utils.log_warning(f'TBA TIM Calculation on {out["match_number"]} missing match data')
            continue
        # Get robot number (e.g. the `i` in  initLineRobot1) and alliance color for TIM
        number_result = utils.catch_function_errors(
            get_robot_number_and_alliance, out['team_number'], quals_matches[out['match_number']]
        )
        # `utils.catch_function_errors` returns `None` for errors, which must be handled before
        # assigning variables to function results.
        if number_result is None:
            continue
        robot_number, alliance = number_result
        for key, values in TBA_SCHEMA['tba'].items():
            filters = copy.deepcopy(values)
            type_ = filters.pop('type')
            if type_ != 'bool':
                utils.log_warning(f'Type {type_} not recognized, skipping...')
                break
            for name, correct_value in values.items():
                # Detect entries like initLineRobot, which need a robot number after them
                if name.endswith('Robot'):
                    del filters[name]
                    filters[f'{name}{robot_number}'] = correct_value
            result = utils.catch_function_errors(
                calc_tba_bool, quals_matches[out['match_number']], alliance, filters
            )
            if result is not None:
                out[key] = result
            else:
                break
        else:
            output_data.append(out)
    return output_data


TBA_SCHEMA = utils.read_schema('schema/calc_tba_tim_schema.yml')
