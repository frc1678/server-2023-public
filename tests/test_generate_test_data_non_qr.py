import argparse
import string
import sys
import os
import random
import yaml

from generate_test_data_non_qr import DataGenerator, parse_args


class TestDataGenerator:
    def setup_method(self):
        input_filename = "schema/calc_predicted_aim_schema.yml"
        self.generate_data = DataGenerator(input_filename, 0)

    def test_import_yaml_struct(self):
        assert isinstance(self.generate_data.import_yaml_struct(), dict)

    def test_generate_json(self):
        assert isinstance(self.generate_data.generate_json(), dict)

    def test_traverse_struct(self):
        _dict = {"test": "int", "test2": {"hey": "int", "hey2": "bool", "hey3": "str"}}
        assert isinstance(self.generate_data.traverse_struct(_dict), dict)
        assert isinstance(_dict["test"], int)
        assert isinstance(_dict["test2"]["hey"], int)
        assert isinstance(_dict["test2"]["hey2"], bool)
        assert isinstance(_dict["test2"]["hey3"], str)

        assert _dict["test"] == 49
        assert _dict["test2"]["hey"] == 49
        assert _dict["test2"]["hey2"] == True
        assert _dict["test2"]["hey3"] == "yyyyyyyyyyyyyyyyyyyyyy"

    def test_return_json(self):
        output_json = self.generate_data.return_json()
        assert isinstance(output_json, dict)

    def test_write_json(self):
        output_filename = "tests/test.json"
        self.generate_data.write_json(output_filename)
        # Check the file exists
        with open(output_filename) as file:
            assert file.read() != ""
        # Remove the file after the test
        os.remove(output_filename)


def test_parse_args():
    sys.argv = [
        'generate_test_data_non_qr.py',
        '-i',
        'schema/calc_predicted_aim_schema.yml',
        '-o',
        'tests/test.json',
    ]
    parsed = parse_args()
    assert parsed.i == sys.argv[2]
    assert parsed.o == sys.argv[4]
