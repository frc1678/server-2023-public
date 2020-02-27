#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Export data from local MongoDB database to CSV file for picklist editor spreadsheet.

Timestamps files. Data exports also used for analysts in stands at competition.
"""
# External imports
import csv
import base64
import datetime
import os
import re
# Internal imports
import adb_communicator
import local_database_communicator
import utils

TEAM_DATA = local_database_communicator.read_dataset('raw.obj_pit')
TEAM_DATA += local_database_communicator.read_dataset('raw.subj_pit')
TEAM_DATA += local_database_communicator.read_dataset('processed.calc_subj_team')
TEAM_IN_MATCH_DATA = local_database_communicator.read_dataset('processed.calc_obj_tim')


def format_header(collection_data, first_keys):
    """Organizes the keys of the documents to be exported into a list of column titles.

    collection_data is the type of data. first_keys are the keys that need to be the first columns
    in the spreadsheet
    """
    # All the keys that will be used to write headers in the CSV file. set() prevents duplicates.
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


def export_team_data():
    """Takes data team data and writes to CSV.
    Merges raw and processed team data into one dictionary
    Puts team export files into their own directory
    to separate them from team in match export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    column_headers = format_header(TEAM_DATA, ['team_number'])
    # The list of teams, used to merge raw and processed team data
    team_set = set()

    # Add team number to a set of teams
    for document in TEAM_DATA:
        team = document.get('team_number')
        team_set.add(team)

    timestamp = datetime.datetime.now()
    # Creates a new CSV file, names it after the type of data and timestamp
    with open(utils.create_file_path(f'data/exports/team_export_{timestamp}.csv'),
              'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        for team in team_set:
            # The dictionary that will hold the combined team data, reset for each team
            merged_team = {}
            # Go through all dictionaries and check if their team number matches the team's
            for document in TEAM_DATA:
                if document.get('team_number') == team:
                    # Update data from the same team to the merged_team dict
                    merged_team.update(document)
            # Use each team's merged data to write a row
            csv_writer.writerow(merged_team)
    utils.log_info('Exported team data to CSV')


def export_tim_data():
    """Takes team in match data and writes to CSV.
    Puts team in match export files into their own directory to separate
    them from team export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    column_headers = format_header(TEAM_IN_MATCH_DATA, ['team_number', 'match_number'])

    # Creates a new CSV file, names it after the type of data and timestamp
    timestamp = datetime.datetime.now()
    with open(utils.create_file_path(
            f'data/exports/team_in_match_export_{timestamp}.csv'),
              'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        # Write rows using data in dictionary
        for document in TEAM_IN_MATCH_DATA:
            csv_writer.writerow(document)
    utils.log_info('Exported TIM to CSV')


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
    for device in os.listdir('data/tablets'):
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


def encode_image_row(team_num, image_paths):
    """Returns the CSV row for a team."""
    row = [team_num]
    ordered_paths = []
    for image_type in IMAGE_ORDER:
        # TODO handle missing pictures
        if not image_paths[image_type]:
            ordered_paths.append('MISSING')
        # If only one picture exists, item will be represented as a string
        elif isinstance(image_paths[image_type], str):
            ordered_paths.append(image_paths[image_type])
        # If multiple exist, item will be represented as an iterable
        else:
            ordered_paths.extend(image_paths[image_type])
    for path in ordered_paths:
        if path == 'MISSING':
            row.append(path)
            continue
        with open(path, 'rb') as file:
            # Add the base64 encoded contents of the file to row
            # The contents must be encoded (in ASCII) because b64encode returns a bytes object
            row.append(base64.b64encode(file.read()).decode('ascii'))
    return row


def write_team_pictures(file):
    """Writes team pictures to `file`."""
    csv_rows = get_image_paths()
    with open(file, 'w') as file:
        writer = csv.writer(file)
        for team_number, paths in csv_rows.items():
            writer.writerow(encode_image_row(team_number, paths))


# Compiles pattern object so it can be used to match the possible image paths
PATH_PATTERN = re.compile(r'([0-9]+)_(full_robot|drivetrain|mechanism_[0-9]+)\.jpg')
IMAGE_ORDER = ['full_robot', 'drivetrain', 'mechanism']
with open('data/team_list.csv') as team_list:
    # Load team list
    TEAMS_LIST = list(csv.reader(team_list))[0]


# Export all data
export_team_data()
export_tim_data()
write_team_pictures('data/exports/robot_images.csv')
