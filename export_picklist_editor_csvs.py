#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Export data from local MongoDB database to CSV file for picklist editor spreadsheet.

Timestamps files. Data exports also used for analysts in stands at competition.
"""
# External imports
import csv
import datetime
# Internal imports
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
    with open(utils.create_file_path(f'data/exports/team_export/team_export_{timestamp}.csv'),
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
            f'data/exports/team_in_match_export/team_in_match_export_{timestamp}.csv'),
              'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        # Write rows using data in dictionary
        for document in TEAM_IN_MATCH_DATA:
            csv_writer.writerow(document)
    utils.log_info('Exported TIM to CSV')

# Export all data
export_team_data()
export_tim_data()
