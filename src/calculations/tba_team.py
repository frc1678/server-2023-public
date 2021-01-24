#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Runs team calculations dependent on TBA data"""

from calculations import inner_goals_regression
from data_transfer import local_database_communicator as ldc
import utils


def calculate_avg_climb_successful_time(obj_tims, tba_tims):
    """Finds the average time for successful climbs in the given tims. Returns 0 for no climbs"""
    successful_climbs = [tim['match_number'] for tim in tba_tims if tim['climb']]
    climb_times = [
        tim['climb_time']
        for tim in obj_tims
        if tim['match_number'] in successful_climbs and 'climb_time' in tim
    ]
    return utils.avg(climb_times)


def tim_counts(obj_tims, tba_tims):
    """Gets the counts for each schema entry for the given tims"""
    matches = {}
    # Split tims by match for each team and combine TBA and scouted data
    for tim in obj_tims + tba_tims:
        if tim['match_number'] in matches:
            matches[tim['match_number']].update(tim)
        else:
            matches[tim['match_number']] = tim
    out = {}
    for name, keys in SCHEMA['counts'].items():
        count = 0
        schema_entry = keys['tim_fields']
        for match in matches.values():
            # Check for TBA TIM and objective TIM fields in the match
            # Skip match if either field is missing to avoid inaccurate data
            if not ('auto_line' in match and 'tele_balls_high' in match):
                continue
            for key, value in schema_entry.items():
                # Handle `not` field
                if isinstance(value, dict) and 'not' in value:
                    # Avoid crashing if tim is missing a value by using `.get` and setting the
                    # default such that if `name` is not in the TIM, then `.get` will return the
                    # value that should not be True, and the loop will `break`
                    if match.get(key, value['not']) == value['not']:
                        break
                else:
                    # Similarly to the previous case, use `.get` to avoid crashing. However, here,
                    # the default value is set to be the opposite of the boolean representation,
                    # such that it will never equal the target value
                    if match.get(key, not value) != value:
                        break
            else:
                # `for` loop exited normally, so all values matched what they are supposed to, so
                # the `count` should be incremented
                count += 1
        out[name] = count
    return out


def update_team_calcs(refs):
    """Returns updates to team calculations based on refs"""
    # Don't try to run calculations if there are no changes
    if not refs:
        return []

    teams_api_endpoint = f'event/{utils.TBA_EVENT_KEY}/teams/simple'
    team_request_output = ldc.select_tba_cache(teams_api_endpoint).get('data', [])
    team_names = {team['team_number']: team['nickname'] for team in team_request_output}

    # Get unique team list
    teams = set()
    tba_team_updates = {}
    for r in refs:
        teams.add(r['team_number'])
    # Run inner goal regression, set to empty dictionary if calculation errors out
    auto_regression_results = utils.catch_function_errors(
        inner_goals_regression.inner_goal_proportions, stage='auto'
    )
    if auto_regression_results is None:
        auto_regression_results = {}
    tele_regression_results = utils.catch_function_errors(
        inner_goals_regression.inner_goal_proportions, stage='tele'
    )
    if tele_regression_results is None:
        tele_regression_results = {}

    for team in teams:
        # Load team data from database
        obj_tims = ldc.read_dataset('processed.calc_obj_tim', team_number=team)
        tba_tims = ldc.read_dataset('processed.calc_tba_tim', team_number=team)
        obj_team = ldc.read_dataset('processed.calc_obj_team', team_number=team)
        if obj_team:
            obj_team = obj_team[0]  # Because of database structure, returns as a list
        else:
            continue  # If objective team calcs are missing, running calcs risks inaccurate outputs

        team_data = tim_counts(obj_tims, tba_tims)
        team_data['team_number'] = team
        team_data['climb_all_success_avg_time'] = calculate_avg_climb_successful_time(
            obj_tims, tba_tims
        )
        if obj_team['climb_all_attempts'] > 0:
            team_data['climb_percent_success'] = (
                team_data['climb_all_successes'] / obj_team['climb_all_attempts']
            )
        else:
            team_data['climb_percent_success'] = 0
        # Load team names
        if team in team_names:
            team_data['team_name'] = team_names[team]
        else:
            # Set team name to "UNKNOWN NAME" if the team is not already in the database
            # If the team is, it is assumed that the name in the database will be more accurate
            if not ldc.read_dataset('processed.calc_tba_team', team_number=team):
                team_data['team_name'] = 'UNKNOWN NAME'
            # Warn that the team is not in the team list for event if there is team data
            if team_names:
                utils.log_warning(f'Team {team} not found in team list from TBA')

        # If regression fails or team is not found, percent inner will default to 0
        team_data['auto_high_balls_percent_inner'] = auto_regression_results.pop(team, 0)
        team_data['tele_high_balls_percent_inner'] = tele_regression_results.pop(team, 0)
        tba_team_updates[team] = team_data
    # Add remaining regression results as regression can change for every team, so data must be
    # updated for every team
    for team, percent in auto_regression_results.items():
        tba_team_updates[team] = {'auto_high_balls_percent_inner': percent, 'team_number': team}
    for team, percent in tele_regression_results.items():
        tba_team_updates[team]['tele_high_balls_percent_inner'] = percent
    return list(tba_team_updates.values())


# Get the last section of each entry (so foo.bar.baz becomes baz)
SCHEMA = utils.unprefix_schema_dict(utils.read_schema('schema/calc_tba_team_schema.yml'))
