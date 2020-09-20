#!/usr/bin/env python3
# Copyright (c) 2020 FRC Team 1678: Citrus Circuits
"""Figures out the ratio of inner goals divided by high goals for each team,

given the number of high goals every team scores in each AIM (Alliance In Match) and the total
number of inner and outer goals scored by the AIM (which comes from TBA).
"""

import copy
import random

import numpy as np

import local_database_communicator as ldc
import utils


def least_squares(A, b, cap_0_to_1=False):
    """Returns the column vector x such that the magnitude of the error vector is minimized,

    where the error vector is Ax-b. x is the best (least square error) solution to the matrix
    equation Ax=b. Since Ax is as close as possible to b, Ax-b is orthogonal to the column space
    of A, therefore Ax-b is in the nullspace of A.t-pose. That means that
    A.t-pose * (Ax - b) = 0, which simplifies to x = (A.t-pose * A)^(-1) * A.t-pose * b

    This is sort of like a system of 200 equations with only 50 variables, so you have to find
    values for the variables such that none of the equations are completely off; they're only
    kind of off.

    cap_0_to_1 says whether all the elements of x will be between 0 and 1. If cap_0_to_1 is True
    use a Monte Carlo method to minimize total square error while keeping proportions between zero
    and one
    """
    if np.linalg.det(A.transpose().dot(A)) == 0:
        raise ValueError(f'Matrix A results in A.t-pose()*A being singular.\nA={A}')
    x = np.linalg.inv(A.transpose().dot(A)).dot(A.transpose()).dot(b)
    if np.isnan(x).any() or np.isinf(x).any():
        # NumPy often returns NaN instead of erroring when something goes wrong
        # We don't like that
        raise Exception(f'Least-squares method returned matrix containing NaN or infinity:\nx={x}')
    if cap_0_to_1 is False:
        return x
    # If cap_0_to_1 is true, use a Monte Carlo algorithm instead of a regression
    x = np.clip(x, 0, 1)
    # Try 10000 times to make tiny random adjustments to x
    for i in range(0, 10000):
        # Make a random modification to x, and store the modified version of x as new_x
        new_x = copy.deepcopy(x)
        rand_index = random.randint(0, len(x) - 1)
        new_x[rand_index, 0] += random.uniform(-.01, .01)
        # Check to see if that change was an improvement
        old_error_vector = A.dot(x) - b
        old_error_magnitude = old_error_vector.transpose().dot(old_error_vector)[0, 0]
        new_error_vector = A.dot(new_x) - b
        new_error_magnitude = new_error_vector.transpose().dot(new_error_vector)[0, 0]
        if new_error_magnitude < old_error_magnitude and (new_x == np.clip(new_x, 0, 1)).all():
            x = new_x
    return x


def inner_goal_proportions(stage='tele'):
    """Returns the ratio of total inner goals to total high goals scored by a given team.

    team_num (int) is the team to be calculated, and stage (str) is either 'auto' or 'tele'.
    """
    # Our schema use 'auto'/'tele', but TBA uses 'auto'/'teleop'
    tba_stage = 'teleop' if stage == 'tele' else 'auto'
    # Begin by getting the teams list, TBA data for every AIM, & scout data for each AIM
    aims = []
    api_url = f'event/{utils.TBA_EVENT_KEY}/matches'
    matches = ldc.select_tba_cache(api_url)[api_url]['data']
    matches = [match for match in matches if match['comp_level'] == 'qm']
    for match in matches:
        for alliance in ['red', 'blue']:
            aim_info = {}
            aim_info['outer_goals'] = match['score_breakdown'][alliance][f'{tba_stage}CellsOuter']
            aim_info['inner_goals'] = match['score_breakdown'][alliance][f'{tba_stage}CellsInner']
            aim_info['team_high_goals'] = {}
            for team in match['alliances'][alliance]['team_keys']:
                # team will be given as a string beginning with frc, eg 'frc701'
                team = team.split('frc')[1]
                match_number = match['match_number']
                # There should only be one TIM for this team in this match
                tims = ldc.read_dataset(
                    'processed.calc_obj_tim', team_number=int(team), match_number=match_number)
                if len(tims) == 1:
                    aim_info['team_high_goals'][team] = tims[0][f'{stage}_balls_high']
                else:
                    print(f'Uh-oh. Found {len(tims)} TIMs for team {team} in match {match_number}')
            aims.append(aim_info)
    # At this point, aims is a list of dictionaries, and each dictionary represents one AIM
    # For example, one AIM might be represented by
    # {'outer_goals': 42, 'inner_goals': 18, 'team_high_goals': {'118': 20, '694': 20, '3132': 20}}
    teams = set()
    for aim in aims:
        for team in aim['team_high_goals'].keys():
            teams.add(team)
    # Ignore teams that didn't score any high goals, since they will mess up the matrix math later
    teams_that_didnt_score = set()
    for team in teams:
        if sum([aim['team_high_goals'].get(team, 0) for aim in aims]) == 0:
            teams_that_didnt_score.add(team)
    teams_that_scored = teams - teams_that_didnt_score
    teams = list(teams)
    teams_that_scored = list(teams_that_scored)
    teams_that_didnt_score = list(teams_that_didnt_score)
    # Create matrices from parameters
    aim_high_goals = np.zeros([len(aims), len(teams_that_scored)])
    # aim_high_goals is a table of team numbers (in the columns) and AIMs (in the rows)
    # Each entry in aim_high_goals is 0 if the team is not in the AIM, and if they are, then the
    # entry is the number of high goals they scored in the AIM
    for i in range(len(aims)):
        for j in range(len(teams_that_scored)):
            aim_high_goals[i, j] = aims[i]['team_high_goals'].get(teams_that_scored[j], 0)
    # inner_goals is a column vector, with each entry representing the total number of inner goals
    # for one AIM
    inner_goals = []  # will be converted to a column vector later
    for aim in aims:
        total_scouted_high_goals = sum(aim['team_high_goals'].values())
        total_actual_high_goals = aim['outer_goals'] + aim['inner_goals']
        # Use the ratio total_scouted_high_goals / total_actual_high_goals to scale AIM inner goals
        # Avoid getting a divide by zero error:
        if total_actual_high_goals == 0:
            inner_goals.append(0)
        else:
            inner_goals.append(
                aim['inner_goals'] * total_scouted_high_goals / total_actual_high_goals)
    inner_goals = np.matrix([inner_goals]).transpose()
    proportions = least_squares(aim_high_goals, inner_goals, cap_0_to_1=True)
    # catch NaN before returning
    if np.isnan(proportions).any() or np.isinf(proportions).any():
        raise Exception(f'NaN or infinity exists in the following vector:\n{proportions}')
    # Cast column vector to list:
    proportions = proportions.transpose().tolist()[0]
    # Return dictionary of team number to their inner-goal-to-high-goal ratio
    inner_goals_dict = {int(team): ratio for (team, ratio) in zip(teams_that_scored, proportions)}
    for team in teams_that_didnt_score:
        inner_goals_dict[int(team)] = 0.
    return inner_goals_dict
