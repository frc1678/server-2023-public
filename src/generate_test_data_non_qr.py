#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Generate test data for non-QRs"""

import argparse
from calculations.generate_random_value import generate_random_value
import utils


class DataGenerator:
    """Given a schema file, find and fill in all the datapoints with random
    data for testing

    1. Given a schema file name, find the collections of datapoints that
    need data to be generated for them
    2. Reformat the "data" datapoint collection to the TUD Structure format
    3. Go through the TUD Structure containing the datapoint collections and
    generate data for each datapoint
    4. Get a number or raw data structures in need or generation and return a
    list of them with get_data()

    generate_data = DataGenerator("<schema_file_path>")

    schema file path must follow sytax of the utils.read_schema()
    format is "schema/<schema_filename>.yml"

    data = generate_data.get_data(<number_of_data>)

    data will be a list of dictionary's that are datapoint field filled in
    with auto generated data
    """

    def __init__(self, schema_filename: str, seed=None):
        """Get schema filename and seed for generation"""
        self.seed = seed
        self.schema_filename = schema_filename

    def open_schema_file(self, schema_filename: str) -> dict:
        """Get schema file name and return opened schema"""
        schema = utils.read_schema(schema_filename)
        return schema

    def get_datapoint_collections_generation(self) -> dict:
        """Get the items from the schema with the two different types of
        structures and convert them to the one that can be processed in the
        function generate_for_each_datapoint_collection()
        The idea here is to generalize the structure to make generation more
        consistent and to have it work with any schema file
        """
        schema = self.open_schema_file(self.schema_filename)

        """Gets collections of datapoints that have the following syntax
        structure

        I coin the following unnamed syntax structure the "Type Under Datapoint
        Structure" or the TUD Structure. The structure is explicitly shown in
        it's json form but also includes a yaml for shown in different schema
        files

        "datapoint_collection": {
            "datapoint_1": {
                "type": <type>
            },
            "datapoint_2": {
                "type": <type>
            }
        }

        With the TUD Structures, it will select the collections of datapoints
        it needs to generate for.

        This shows an example Structure before and after it goes through and
        selects the points it will generate data for
        {
            "schema_file": {},
            "data": {},
            "averages": {},
            "counts": {},
        }

        ->

        {
            "averages": {},
            "counts": {},
        }

        """
        # TUD Structure format of datapoint collections
        datapoint_collections = {}
        for key, value in schema.items():
            # "schema_file" is not needed and "data" is in TVD Structure format
            # Later, "data" will be converted into TUD Structure format
            if key not in ["schema_file", "data", "schema"]:
                datapoint_collections[key] = value

        """Convert structure of the "data" datapoint collection to TUD
        Structure

        I coin this structure the "Type as Value Datapoint Structure" or the
        TVD Structure

        "data" {
            "datapoint_1": <type>,
            "datapoint_2": <type>,
        }
        """
        # Convert data (TVD Structure format) to a TUD Structure format
        # This will only happen if "data" is in the schema file
        if schema.get("data") is not None:
            new_data = {}
            for key, value in schema["data"].items():
                new_data[key] = {"type": value}

            """Now that "data": {} has been formatted into the TUD Structure,
            it can be added to the other parts already in the TUD Structure
            {
                "averages": {},
                "counts": {},
                "data": {}
            }
            """

            datapoint_collections["data"] = new_data

        if schema.get("schema") is not None:
            new_schema = {}
            for key, value in schema["schema"].items():
                new_schema[key] = {"type": value}

            datapoint_collections["schema"] = new_schema

        return datapoint_collections

    def generate_for_each_datapoint_collection(self) -> dict:
        """Go through the dictionary with all the datapoint collections and
        then go through all the datapoints inside those collections. After this
        get the type listed under the datapoint and generate a value for it
        """
        datapoint_collections = self.get_datapoint_collections_generation()

        generated_structure = {}

        # Go through each datapoint collection
        for (
            datapoint_collection_names,
            datapoint_collection_values,
        ) in datapoint_collections.items():

            # Go through each datapoint in the datapoint collections
            for (
                datapoints_values_key,
                datapoints_values_value,
            ) in datapoint_collection_values.items():
                if datapoints_values_value.get("type") is not None:
                    value_type = datapoints_values_value["type"]
                    if value_type != "Enum":
                        # Generate value based on the value_type
                        datapoint = generate_random_value(value_type, self.seed)
                        generated_structure[datapoints_values_key] = datapoint
                    else:
                        generated_structure[datapoints_values_key] = 1

        return generated_structure

    def format_raw_data(self) -> dict:
        """Get the data and format it correctly"""
        data = self.generate_for_each_datapoint_collection()
        # TODO: make sure the format is correct, fix needed
        return data

    def request_single_data_struct(self) -> dict:
        """Important to be a single item of data returned as a dict instead of
        needing to request a list, and getting items from it"""
        return self.format_raw_data()

    def get_data(self, times: int = 1) -> list:
        """Send requests for a single thing of data, return as many as
        requested as a list"""
        list_of_data = []
        for num in range(times):
            data = self.request_single_data_struct()
            list_of_data.append(data)
        return list_of_data


def name_sample_data(filename: str, number_of_data: int):
    """Return the data with a name for easy demonstration of data"""
    generate_data = DataGenerator(filename)
    data = generate_data.get_data(number_of_data)
    return {filename: data[0]}


def parse_args():
    """Parse out the needed args"""
    parser = argparse.ArgumentParser()
    # Add arguments for input and output
    parser.add_argument(
        "-i",
        help="Input schema file; e.g. schema/calc_subj_team_schema.yml",
        required=True,
    )
    parser.add_argument(
        "-n",
        help="Number of data structures; e.g. 2",
        required=True,
    )
    parsed = parser.parse_args()
    return parsed


if __name__ == "__main__":
    """This script is both something that can be imported and used in the
    command line (import instructions at top of class)

    CLI instructions; use -h option for detail
    python3 generate_test_data_non_qr.py -i <input_schema_file> -n <number_of_data>

    The input_schema_file uses the same syntax as utils.read_schema
    "schema/<schema_file_name>.yml"

    The number_of_data is an int of how many raw data structures you want
    """
    parsed = parse_args()

    # Set filenames
    input_filename = parsed.i
    number_of_data = int(parsed.n)

    generate_data = DataGenerator(input_filename)
    data = generate_data.get_data(number_of_data)
    print(data)
