#!/usr/bin/env python3
# Copyright (c) 2020 FRC Team 1678: Citrus Circuits
"""Holds variables + functions that are shared across server files."""
# External imports
import logging
import os
import subprocess
import traceback
# No internal imports


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


def catch_function_errors(fn, *args, **kwargs):
    """Returns function return value or None if there are errors"""
    try:
        result = fn(*args, **kwargs)
    # Keyboard interrupts should stop server
    except KeyboardInterrupt:
        raise
    # Notify user that error occurred
    except Exception as err:
        logging.error(f'{err}\n{"".join(traceback.format_stack()[:-1])}')
        print(f'Function {fn.__name__}: {err.__class__} - {err}')
        result = None
    return result


def save_event_key(tba_event_key):
    """Saves event key in data/tba_event_key.txt"""
    with open(_TBA_KEY_FILE, 'w') as file:
        file.write(tba_event_key)


def log_warning(warning):
    """Logs warnings to server.log

    'warning' is the warning message
    Logs to server.log in this directory
    """
    # Logs warning, also contains a traceback
    logging.warning(f'{warning}\n{"".join(traceback.format_stack()[:-1])}')
    # Prints warning to console
    print(f'WARNING: {warning}')


def run_command(command, return_output=False):
    """Runs a command using subprocess.
    command (string) is the terminal command to be run
    returns the standard output of the command if return_output is True
    """
    # We use .split(' ') because subprocess.run() expects the command as a list of strings
    # Example, .run(['echo', 'hello']) instead of .run('echo hello')
    command = command.split(' ')
    if return_output is True:
        output = subprocess.run(command, check=True, stdout=subprocess.PIPE).stdout
        # output is a byte-like string and needs to be decoded
        # Remove trailing newlines
        output = output.decode('utf-8').rstrip('\n')
        # Replace '\r\n' with '\n' to match the UNIX format for newlines
        output = output.replace('\r\n', '\n')
        return output
    subprocess.run(command, check=True)
    return None


def avg(nums, weights=None, default=0):
    """Calculates the average of a list of numeric types

    If the optional parameter weights is given, calculates a weighted average
    weights should be a list of floats
    The length of weights must be the same as the length of nums
    default is the value returned if nums is an empty list
    """
    if len(nums) == 0:
        return default
    if weights is None:
        # Normal (not weighted) average
        return sum(nums) / len(nums)
    # Expect one weight for each number
    if len(nums) != len(weights):
        raise ValueError(f'Weighted average expects one weight for each number.')
    weighted_sum = sum([num * weight for num, weight in zip(nums, weights)])
    return weighted_sum / sum(weights)


_TBA_KEY_FILE = 'data/competition.txt'

# The directory this script is located in
MAIN_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# Set the basic config for logging functions
logging.basicConfig(filename='server.log', filemode='a', format='%(asctime)s %(message)s')

try:
    # Specifies which event - string such as '2020cada'.
    with open(create_file_path(_TBA_KEY_FILE)) as file:
        # Remove trailing newline (if it exists) from file data.
        # Many file editors will automatically add a newline at the end of files.
        TBA_EVENT_KEY = file.read().rstrip('\n')
except FileNotFoundError:
    log_warning(f'ERROR Loading TBA Key: File {_TBA_KEY_FILE} NOT FOUND')
