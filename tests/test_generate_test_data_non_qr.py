import sys
import pytest
import utils

import generate_test_data_non_qr
from generate_test_data_non_qr import DataGenerator, parse_args

CORRECT_SCHEMA_DATAPOINT_COLLECTIONS = [
    {
        'auto_avg_balls_low': 84.4422,
        'auto_avg_balls_high': 84.4422,
        'auto_avg_balls_total': 84.4422,
        'tele_avg_balls_low': 84.4422,
        'tele_avg_balls_high': 84.4422,
        'tele_avg_balls_total': 84.4422,
        'avg_incap_time': 84.4422,
        'tele_cp_rotation_successes': 49,
        'tele_cp_position_successes': 49,
        'climb_all_attempts': 49,
        'team_number': 49,
    },
    {
        'auto_balls_low': 49,
        'auto_balls_high': 49,
        'tele_balls_low': 49,
        'tele_balls_high': 49,
        'control_panel_rotation': True,
        'control_panel_position': True,
        'incap': 49,
        'climb_time': 49,
        'confidence_rating': 49,
        'team_number': 49,
        'match_number': 49,
    },
    {'first_pick_ability': 84.4422, 'second_pick_ability': 84.4422, 'team_number': 49},
    {
        'predicted_score': 84.4422,
        'predicted_rp1': 84.4422,
        'predicted_rp2': 84.4422,
        'match_number': 49,
        'alliance_color_is_red': True,
    },
    {
        'predicted_rps': 84.4422,
        'predicted_rank': 49,
        'team_number': 49,
        'current_rank': 49,
        'current_rps': 49,
        'current_avg_rps': 84.4422,
    },
    {
        'driver_agility': 84.4422,
        'driver_rendezvous_agility': 84.4422,
        'driver_ability': 84.4422,
        'team_number': 49,
    },
    {
        'auto_high_balls_percent_inner': 84.4422,
        'tele_high_balls_percent_inner': 84.4422,
        'climb_all_success_avg_time': 84.4422,
        'team_name': 'yyyyyyyyyyyyyyyyyyyyyy',
        'climb_percent_success': 84.4422,
        'climb_all_successes': 49,
        'climb_level_successes': 49,
        'park_successes': 49,
        'auto_line_successes': 49,
        'team_number': 49,
    },
    {'auto_line': True, 'climb': True, 'park': True, 'level_climb': True},
    {
        'team_number': 49,
        'can_cross_trench': True,
        'drivetrain': 1,
        'drivetrain_motors': 49,
        'drivetrain_motor_type': 1,
        'has_ground_intake': True,
    },
    {
        'team_number': 49,
        'climber_strap_installation_difficulty': 49,
        'climber_strap_installation_notes': "yyyyyyyyyyyyyyyyyyyyyy",
    },
]


class TestDataGenerator:
    def setup_method(self):
        self.input_filename = "schema/calc_obj_tim_schema.yml"
        self.generate_data = DataGenerator(self.input_filename)

        self.schema_files = utils.get_schema_filenames()
        self.schema_files.remove("match_collection_qr_schema.yml")
        self.schema_files = list(self.schema_files)
        self.schema_files.sort()

    def test_open_schema_file(self):
        schema = self.generate_data.open_schema_file(self.input_filename)
        assert utils.read_schema(self.input_filename) == schema

    def test_get_datapoint_collections_generation(self):
        for schema_file in self.schema_files:
            generate_data = DataGenerator(f"schema/{schema_file}", 0)
            datapoint_collections = generate_data.get_datapoint_collections_generation()
            assert "schema_file" not in datapoint_collections

    def test_generate_for_each_datapoint_collection(self):
        pytest.xfail('Fails under current schema; will be fixed by future PR')
        for num, schema_file in enumerate(self.schema_files):
            generate_data = DataGenerator(f"schema/{schema_file}", 0)
            generated_structure = generate_data.generate_for_each_datapoint_collection()
            assert generated_structure == CORRECT_SCHEMA_DATAPOINT_COLLECTIONS[num]

    def test_format_raw_data(self):
        for schema_file in self.schema_files:
            generate_data = DataGenerator(f"schema/{schema_file}", 0)
            formated_raw_data = generate_data.format_raw_data()
            assert isinstance(formated_raw_data, dict)
            assert "schema_file" not in formated_raw_data
            assert "data" not in formated_raw_data

    def test_request_single_data_struct(self):
        for schema_file in self.schema_files:
            generate_data = DataGenerator(f"schema/{schema_file}", 0)
            single_raw_data = generate_data.request_single_data_struct()
            assert isinstance(single_raw_data, dict)
            assert "schema_file" not in single_raw_data
            assert "data" not in single_raw_data

    def test_get_data(self):
        for schema_file in self.schema_files:
            generate_data = DataGenerator(f"schema/{schema_file}", 0)
            for num in range(5):
                list_of_raw_data_structures = generate_data.get_data(num)
                assert isinstance(list_of_raw_data_structures, list)
                assert len(list_of_raw_data_structures) == num


def test_name_sample_data():
    schema_files = utils.get_schema_filenames()
    schema_files.remove("match_collection_qr_schema.yml")
    schema_files = list(schema_files)
    schema_files.sort()

    for schema in schema_files:
        data = generate_test_data_non_qr.name_sample_data(f"schema/{schema}", 1)
        assert isinstance(data, dict)
        assert isinstance(data[f"schema/{schema}"], dict)


def test_parse_args():
    sys.argv = [
        'generate_test_data_non_qr.py',
        '-i',
        'schema/calc_predicted_aim_schema.yml',
        '-n',
        '2',
    ]
    parsed = parse_args()
    assert parsed.i == sys.argv[2]
    assert parsed.n == sys.argv[4]
