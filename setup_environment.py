#!/usr/bin/python3.6
"""Sets up a machine for use or testing of the server.

To be run for every new clone of server-2020.
"""
# No external imports
# Internal imports
import utils

# Creates data folder
utils.create_file_path('data/')
