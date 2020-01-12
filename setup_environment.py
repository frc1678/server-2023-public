#!/usr/bin/python3.6
"""Sets up a machine for use or testing of the server.

To be run for every new clone of server-2020.
"""
# External imports
import os
import subprocess
import venv
# Internal imports
import utils

# Creates data folder
utils.create_file_path('data/')

# Creates path by joining the base directory and the target directory
TARGET_PATH = utils.create_file_path('.venv', False)

# Only run if file is directly called
if __name__ == '__main__':
    # Create virtual environment
    print('Creating Virtual Environment...')
    # Clear any existing environments with clear=True
    # Install pip directly into installation
    # Set prompt to 'venv' instead of '.venv'
    venv.create(TARGET_PATH, clear=True, with_pip=True, prompt='venv')
    print('Virtual Environment Created')

    # Install pip packages
    # Set create_directories to false to avoid trying to create directory for pip
    if os.name == 'nt':
        # Windows uses a Scripts directory instead of a bin directory
        PIP_PATH = utils.create_file_path('.venv/Scripts/pip', False)
    else:
        PIP_PATH = utils.create_file_path('.venv/bin/pip', False)
    REQUIREMENTS_PATH = utils.create_file_path('requirements.txt')
    print('Installing PyPI Packages...')
    # Runs /path/to/pip install -r /path/to/requirements.txt
    # Sets check to True to force check that pip exited without errors
    # Pipes pip output to /dev/null to avoid cluttering the terminal
    # All pip warnings/errors still print to terminal because stderr is not redirected
    subprocess.run([PIP_PATH, 'install', 'wheel'], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([PIP_PATH, 'install', '-r', REQUIREMENTS_PATH], check=True,
                  stdout=subprocess.DEVNULL)
    print('Environment Setup Complete')
