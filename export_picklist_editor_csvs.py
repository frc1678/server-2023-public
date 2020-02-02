#!/usr/bin/python3.6
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

# Read competition key set by setup_competition.py
KEY = utils.TBA_EVENT_KEY

# Finds all documents matching the competiton key, returns specified fields
# Supresses _id, which isn't exported
TEAM_DATA = local_database_communicator.select_from_database(
    {'tba_event_key': KEY}, {'raw.pit': 1, 'processed.calc_team': 1, '_id': 0})
TEAM_IN_MATCH_DATA = local_database_communicator.select_from_database(
    {'tba_event_key': KEY}, {'processed.consolidated_obj_tim': 1, '_id': 0})


def make_lists(collection_data, first_keys):
    """Puts data from local MongoDB database in list format to be exported

    collection_data contains the fields to be exported. file_name marks the
    type of data in the file to easily distinguish between files and also
    names the directories created for each type of data.
    first_keys are the columns that need to be first in the CSV file. For
    team data, it is team_number. For team in match data, they are
    team_number and match_number so the picklist editor can sort by those
    keys.
    """
    # All the keys that will be used to write headers in the CSV file
    column_headers = set()
    # The list of dictionaries containing data to be exported
    dictionary_list = []
    # Iterate through levels of embedded documents in the collection_data document
    for field in collection_data:
        # Iterate through sections (eg. 'raw')
        for section in field.values():
            # Iterate through the embedded documents (eg. 'pit')
            for value in section.values():
                # Iterate through each set of data
                for dictionary in value:
                    # Add dictionaries of data to a list that will be used to write rows
                    dictionary_list.append(dictionary)
                    # The keys at the lowest level of nesting are the datapoints to be exported
                    for key in dictionary.keys():
                        # Key will become a header to a column containing its values
                        column_headers.add(key)

    # Picklist editor needs match number and team number to be the first columns
    # Moves match and team number to the front of column_headers
    for key in first_keys:
        column_headers.discard(key)
    column_headers = first_keys + list(column_headers)

    return column_headers, dictionary_list


def export_team_data():
    """Takes data in list format from make_lists and writes to CSV.
    Merges raw and processed team data into one dictionary
    Puts team export files into their own directory to separate
    them from team in match export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    column_headers, dictionary_list = make_lists(TEAM_DATA, ['team_number'])
    # The list of teams, used to merge raw and processed team data
    team_set = set()

    # Add team number to a set of teams
    for dictionary in dictionary_list:
        team = dictionary.get('team_number')
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
            for dictionary in dictionary_list:
                if dictionary.get('team_number') == team:
                    # Update data from the same team to the merged_team dict
                    merged_team.update(dictionary)
            # Use each team's merged data to write a row
            csv_writer.writerow(merged_team)


def export_tim_data():
    """Takes data in list format from make_lists and writes to CSV.
    Puts team in match export files into their own directory to separate
    them from export files.
    """
    # Get the lists of column headers and dictionaries to use in export
    column_headers, dictionary_list = make_lists(
        TEAM_IN_MATCH_DATA, ['team_number', 'match_number'])

    # Creates a new CSV file, names it after the type of data and timestamp
    timestamp = datetime.datetime.now()
    with open(utils.create_file_path(
            f'data/exports/team_in_match_export/team_in_match_export_{timestamp}.csv'),
              'w') as file:
        # Write headers using the column_headers list
        csv_writer = csv.DictWriter(file, fieldnames=column_headers)
        csv_writer.writeheader()

        # Write rows using data in dictionary
        for dictionary in dictionary_list:
            csv_writer.writerow(dictionary)

# Export all data
export_team_data()
export_tim_data()
