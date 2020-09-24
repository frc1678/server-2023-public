#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Export data from local MongoDB database to CSV file for picklist editor spreadsheet.

Timestamps files. Data exports also used for analysts in stands at competition.
"""

import base64
import csv
import datetime
import os
import re
import sys

import local_database_communicator
import utils


def load_data(db_paths):
    """Loads team data from database and formats enums, db_paths is a list of database paths."""
    all_data = []
    for path in db_paths:
        data = local_database_communicator.read_dataset(path)
        schema = utils.read_schema(DB_PATH_TO_SCHEMA_FILE[path])
        if 'enums' not in schema:
            all_data.extend(data)
            continue
        for entry in data:
            for name, value in entry.items():
                if name in schema['enums']:
                    for key, val in schema['enums'][name].items():
                        if val == value:
                            entry[name] = key
                            continue
        all_data.extend(data)
    return all_data


def format_header(collection_data, first_keys):
    """Organizes the keys of the documents to be exported into a list of column titles.

    collection_data is the type of data. first_keys are the keys that need to be the first columns
    in the spreadsheet.
    """
    # All the keys that will be used to write headers in the CSV file. set() prevents duplicates
    column_headers = set()
    # Find all the keys of the documents and add them to the column_headers set
    for document in collection_data:
        for key in document.keys():
            column_headers.add(key)

    # Picklist editor needs team number and sometimes match number to be the first columns
    # Moves those datapoints to the front of column_headers
    for key in first_keys:
        column_headers.discard(key)
    column_headers = first_keys + list(column_headers)

    return column_headers


def export_team_data(path):
    """Takes data team data and writes to CSV.
    Merges raw and processed team data into one dictionary
    Puts team export files into their own directory
    to separate them from team in match export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    team_data = load_data(TEAM_DATA_DB_PATHS)
    column_headers = format_header(team_data, ['team_number'])
    # The list of teams, used to merge raw and processed team data

    with open(path, 'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        for team in TEAMS_LIST:
            # The dictionary that will hold the combined team data, reset for each team
            merged_team = {}
            # Go through all dictionaries and check if their team number matches the team's
            for document in team_data:
                if document.get('team_number') == team:
                    # Update data from the same team to the merged_team dict
                    merged_team.update(document)
            # Use each team's merged data to write a row
            csv_writer.writerow(merged_team)
    print('Exported team data to CSV')


def export_tim_data(path):
    """Takes team in match data and writes to CSV. Puts team in match export files into their own

    directory to separate them from team export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    all_tim_data = load_data(TIM_DATA_DB_PATHS)
    column_headers = format_header(all_tim_data, ['match_number', 'team_number'])

    with open(path, 'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        for team in TEAMS_LIST:
            # Write rows using data in dictionary
            team_data = []
            for document in all_tim_data:
                if document['team_number'] == team:
                    team_data.append(document)
            tim_data = {}
            for document in team_data:
                if document['match_number'] in tim_data:
                    tim_data[document['match_number']].update(document)
                else:
                    tim_data[document['match_number']] = document
            for document in tim_data.values():
                csv_writer.writerow(document)
    print('Exported TIM data to CSV')


def get_image_paths():
    """Gets dictionary of image paths"""
    csv_rows = dict()
    for team in TEAMS_LIST:
        # Makes the team key a list with the team number in it.
        csv_rows[team] = {
            'full_robot': '',
            'drivetrain': '',
            'mechanism': [],
        }
    # Iterates through each device in the tablets folder
    for device in os.listdir(utils.create_file_path('data/tablets')):
        # If the device is a phone serial number
        if device not in ['9AQAY1EV7J', '9AMAY1E54G', '9AMAY1E53P']:
            continue
        device_dir = utils.create_file_path(f'data/tablets/{device}/')
        # Iterates through all of files in the phone's folder
        for file in os.listdir(device_dir):
            # Tries to match the file name with the regular expression
            result = re.fullmatch(PATH_PATTERN, file)
            # If the regular expression matched
            if result:
                # Team number is the result of the first capture type
                team_num = result.group(1)
                if team_num not in TEAMS_LIST:
                    continue
                # Photo type is the result of the second capture group
                photo_type = result.group(2)

                # There can be multiple mechanism photos, so we need to handle differently
                if photo_type.startswith('mechanism'):
                    csv_rows[team_num]['mechanism'].append(os.path.join(device_dir, file))
                # Otherwise just add the photo path to its specified place in csv_rows
                else:
                    csv_rows[team_num][photo_type] = os.path.join(device_dir, file)
    return csv_rows


def format_tba_data():
    """Formats TBA score and foul data as CSV."""
    api_url = f'event/{utils.TBA_EVENT_KEY}/matches'
    cached = local_database_communicator.select_tba_cache(api_url)[api_url]['data']
    match_scores = []
    export_fields = ['foulPoints', 'totalPoints']
    for match in cached:
        if match['score_breakdown'] is None or match['comp_level'] != 'qm':
            continue
        for alliance in ['red', 'blue']:
            data = {'match_number': match['match_number'], 'alliance': alliance}
            for field in export_fields:
                data[field] = match['score_breakdown'][alliance][field]
            for i, team in enumerate(match['alliances'][alliance]['team_keys'], start=1):
                data[f'robot{i}'] = int(team[3:])
            match_scores.append(data)
    return sorted(match_scores, key=lambda x: x['match_number'])


def write_tba_data(path):
    """Writes TBA Data to csv export. Path is a str representing the output absolute file path."""
    data = format_tba_data()
    if not data:
        print('No TBA Data to export', file=sys.stderr)
    field_names = data[0].keys()
    with open(path, 'w') as file:
        writer = csv.DictWriter(file, field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print('Exported TBA Data')


def full_data_export():
    """Writes the current export to a timestamped directory. Returns the directory path written"""
    current_time = datetime.datetime.now()
    timestamp_str = current_time.strftime('%Y-%m-%d_%H:%M:%S')
    # Creates directory if it does not exist
    directory_path = utils.create_file_path(f'data/exports/export_{timestamp_str}')
    # Team data
    team_file_path = os.path.join(directory_path, f'team_export_{timestamp_str}.csv')
    export_team_data(team_file_path)
    # Team in match data
    timd_file_path = os.path.join(directory_path, f'timd_export_{timestamp_str}.csv')
    export_tim_data(timd_file_path)
    # TBA match data
    tba_file_path = os.path.join(directory_path, f'tba_export_{timestamp_str}.csv')
    write_tba_data(tba_file_path)
    return directory_path


# Compiles pattern object so it can be used to match the possible image paths
PATH_PATTERN = re.compile(r'([0-9]+)_(full_robot|drivetrain|mechanism_[0-9]+)\.jpg')
IMAGE_ORDER = ['full_robot', 'drivetrain', 'mechanism']

with open('data/team_list.csv') as team_list:
    # Load team list
    TEAMS_LIST = list(map(int, [*csv.reader(team_list)][0]))

TEAM_DATA_DB_PATHS = [
    'raw.obj_pit',
    'raw.subj_pit',
    'processed.calc_obj_team',
    'processed.calc_subj_team',
    'processed.calc_tba_team'
]
TIM_DATA_DB_PATHS = [
    'processed.calc_obj_tim',
    'processed.calc_tba_tim'
]
DB_PATH_TO_SCHEMA_FILE = {
    'raw.obj_pit': 'schema/obj_pit_collection_schema.yml',
    'raw.subj_pit': 'schema/subj_pit_collection_schema.yml',
    'processed.calc_obj_team': 'schema/calc_obj_team_schema.yml',
    'processed.calc_subj_team': 'schema/calc_subj_team_schema.yml',
    'processed.calc_tba_team': 'schema/calc_tba_team_schema.yml',
    'processed.calc_obj_tim': 'schema/calc_obj_tim_schema.yml',
    'processed.calc_tba_tim': 'schema/calc_tba_tim_schema.yml'
}

if __name__ == '__main__':
    EXPORT_PATH = full_data_export()
    LATEST_PATH = utils.create_file_path('data/exports/latest_export', False)
    # Remove latest export directory if it exists
    if os.path.exists(LATEST_PATH):
        os.remove(LATEST_PATH)
    # Symlink the latest_export directory to the export that was just made
    os.symlink(EXPORT_PATH, LATEST_PATH)
