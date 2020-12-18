#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Generate test data for non-QRs"""

import argparse
from calculations import generate_random_value
import json
import random
import yaml


class DataGenerator:
    """Take input filenames and generate json filled with test values

    Take parameters of filenames and load in yaml schema file
    Traverse the loaded structure and fill it with random values
    """

    def __init__(self, input_filename: str, seed=None):
        """Get input filename and return the json"""
        self.seed = seed

        self.input_filename = input_filename
        self.return_json()

    def import_yaml_struct(self):
        """Import the yaml file and load the file"""
        with open(self.input_filename, "r") as yaml_file:
            # Load yaml file as dictionary structure
            yaml_struct = yaml.load(yaml_file, Loader=yaml.FullLoader)
        return yaml_struct

    def generate_json(self):
        """Get yaml_struct and pass it to traverse_struct

        Get the returned yaml structure and traverse said structure.
        Return json with final values in place of type names"""
        yaml_struct = self.import_yaml_struct()
        # Used to copy the imported yaml so the yaml needs to be parsed only once
        # in case we want this script to generate multiple sets of test data
        editable_structure = yaml_struct.copy()
        return self.traverse_struct(editable_structure)

    def traverse_struct(self, dictionary: dict):
        """Recursively traverse dictionary and substitute names values in

        Recursively traverse the dictionary structure and substitute names of data types for
        values that are generated with the function random_value"""
        for key, value in dictionary.items():
            # Check if the value is actually another layer to be traversed
            if isinstance(value, dict):
                # Recurse! and ya know, Recurse!
                self.traverse_struct(dictionary[key])
            # If the value is actually a type, then replace the value with the random_value
            elif value in ["str", "int", "float", "bool"]:
                # Set value to random_value that was generated
                dictionary[key] = generate_random_value.generate_random_value(value, self.seed)
            # Otherwise, don't do anything to the value, it's all good
        return dictionary

    def return_json(self):
        """Return the dictionary as a json"""
        # Generate the json file
        output_struct = self.generate_json()
        return output_struct

    def write_json(self, output_filename: str):
        """Dump the structure to a json file with output_filename"""
        with open(output_filename, "w") as file:
            json.dump(self.return_json(), file)


def parse_args():
    """Parse out the needed args"""
    parser = argparse.ArgumentParser()
    # Add arguments for input and output
    parser.add_argument("-i", help="Input yaml file", required=True)
    parser.add_argument("-o", help="Output json file", required=False)
    parsed = parser.parse_args()
    return parsed


if __name__ == "__main__":
    parsed = parse_args()

    # Set filenames
    input_filename = parsed.i
    output_filename = parsed.o

    # Make and instance and write json
    generate_data = DataGenerator(input_filename)
    generate_data.write_json(output_filename)
