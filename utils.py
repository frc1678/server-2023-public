#!/usr/bin/python3.6
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Holds variables + functions that are shared across server files."""
# External imports
import os
# No internal imports

_TBA_KEY_FILE = 'data/competition.txt'

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


def create_file_path(path_after_main, create_directories=True):
    """Joins the path of the directory this script is in with the path
    that is passed to this function.
    path_after_main is the path from inside the main directory.  For
    example, the path_after_main for server.py would be 'server.py'
    because it is located directly in the main directory.
    create_directories will create the directories in the path if they
    do not exist.  Assumes that all files names include a period, and
    all paths are input in Linux/Unix style.
    create_directories defaults to True.
    """
    # Removes trailing slash in 'path_after_main' (if it exists) and split by '/'
    path_after_main = path_after_main.rstrip('/').split('/')
    if create_directories is True:
        # Checks if the last item in the path is a file
        if '.' in path_after_main[-1]:
            # Only try to create directories if there are directories specified before filename
            if len(path_after_main) > 1:
                # The '*' before the variable name expands the list into arguments for the function
                directories = os.path.join(*path_after_main[:-1])
            # Make directories a blank string
            else:
                directories = ''
        # The last item is a directory
        else:
            directories = os.path.join(*path_after_main)
        # 'os.makedirs' recursively creates directories (i.e. it will
        # Create multiple directories, if needed)
        os.makedirs(os.path.join(MAIN_DIRECTORY, directories), exist_ok=True)
    return os.path.join(MAIN_DIRECTORY, *path_after_main)


def get_bool(value):
    """Get boolean from string"""
    if value.upper() in ["1", "T", "TRUE"]:
        return True
    if value.upper() in ["0", "F", "FALSE"]:
        return False
    raise ValueError(f"Unable to convert {value} to boolean.")


def save_event_key(tba_event_key):
    """Saves event key in data/tba_event_key.txt"""
    with open(_TBA_KEY_FILE, 'w') as file:
        file.write(tba_event_key)


# Specifies which event - string such as '2020cada'.
with open(create_file_path(_TBA_KEY_FILE)) as file:
    # Remove trailing newline (if it exists) from file data.
    # Many file editors will automatically add a newline at the end of files.
    TBA_EVENT_KEY = file.read().rstrip('\n')
