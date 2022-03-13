import sys
import utils

import generate_test_data
from generate_test_data import DataGenerator, parse_args

CORRECT_SCHEMA_DATAPOINT_COLLECTIONS = [
    # Obj Team
    {
        "auto_avg_high_balls": 84.4422,
        "auto_avg_total_balls": 84.4422,
        "tele_avg_high_balls": 84.4422,
        "tele_avg_total_balls": 84.4422,
        "auto_avg_other_high_balls": 84.4422,
        "tele_avg_other_high_balls": 84.4422,
        "auto_avg_hub_high_balls": 84.4422,
        "auto_avg_low_balls": 84.4422,
        "tele_avg_hub_high_balls": 84.4422,
        "tele_avg_low_balls": 84.4422,
        "auto_sd_low_balls": 84.4422,
        "auto_sd_high_balls": 84.4422,
        "tele_sd_low_balls": 84.4422,
        "tele_sd_high_balls": 84.4422,
        "avg_incap_time": 84.4422,
        "avg_intakes": 84.4422,
        "climb_percent_success": 84.4422,
        "high_rung_successes": 49,
        "lfm_auto_avg_high_balls": 84.4422,
        "lfm_auto_avg_hub_high_balls": 84.4422,
        "lfm_auto_avg_low_balls": 84.4422,
        "lfm_auto_avg_other_high_balls": 84.4422,
        "lfm_auto_max_high_balls": 49,
        "lfm_auto_max_low_balls": 49,
        "lfm_avg_incap_time": 84.4422,
        "lfm_climb_all_attempts": 49,
        "lfm_climb_percent_success": 84.4422,
        "lfm_high_rung_successes": 49,
        "lfm_low_rung_successes": 49,
        "lfm_matches_incap": 49,
        "lfm_max_climb_level": "yyyyyyyyyyyyyyyyyyyyyy",
        "lfm_max_incap": 49,
        "lfm_mid_rung_successes": 49,
        "lfm_mode_start_position": None,
        "lfm_tele_avg_high_balls": 84.4422,
        "lfm_tele_avg_low_balls": 84.4422,
        "lfm_tele_avg_hub_high_balls": 84.4422,
        "lfm_tele_avg_other_high_balls": 84.4422,
        "lfm_tele_max_high_balls": 49,
        "lfm_tele_max_low_balls": 49,
        "lfm_traversal_rung_successes": 49,
        "low_rung_successes": 49,
        "matches_incap": 49,
        "max_climb_level": "yyyyyyyyyyyyyyyyyyyyyy",
        "mid_rung_successes": 49,
        "mode_climb_level": None,
        "mode_start_position": None,
        "traversal_rung_successes": 49,
        "climb_all_attempts": 49,
        "matches_played": 49,
        "team_number": 49,
        "auto_max_low_balls": 49,
        "auto_max_high_balls": 49,
        "tele_max_low_balls": 49,
        "tele_max_high_balls": 49,
        "max_incap": 49,
        "position_zero_starts": 49,
        "position_four_starts": 49,
        "position_one_starts": 49,
        "position_three_starts": 49,
        "position_two_starts": 49,
        "matches_played_defense": 49,
        "avg_climb_points": 84.4422,
    },
    # Obj TIM
    {
        "confidence_rating": 49,
        "match_number": 49,
        "team_number": 49,
        "auto_hub_high_balls": 49,
        "auto_other_high_balls": 49,
        "auto_low_balls": 49,
        "tele_hub_high_balls": 49,
        "tele_other_high_balls": 49,
        "tele_low_balls": 49,
        "auto_high_balls": 49,
        "tele_high_balls": 49,
        "auto_total_balls": 49,
        "tele_total_balls": 49,
        "incap": 49,
        "intakes": 49,
        "climb_attempts": 49,
        "climb_level": "yyyyyyyyyyyyyyyyyyyyyy",
        "start_position": "yyyyyyyyyyyyyyyyyyyyyy",
    },
    # Pickability
    {
        "first_pickability": 84.4422,
        "second_pickability": 84.4422,
        "test_first_pickability": 84.4422,
        "test_second_pickability": 84.4422,
        "team_number": 49,
    },
    # Predicted AIM
    {
        "predicted_score": 84.4422,
        "predicted_rp1": 84.4422,
        "predicted_rp2": 84.4422,
        "match_number": 49,
        "alliance_color_is_red": True,
        "has_actual_data": True,
        "actual_score": 49,
        "actual_rp1": 84.4422,
        "actual_rp2": 84.4422,
        "won_match": True,
        "final_predicted_score": 84.4422,
        "final_predicted_rp1": 84.4422,
        "final_predicted_rp2": 84.4422,
        "has_final_scores": True,
    },
    # Predicted Team
    {
        "predicted_rps": 84.4422,
        "predicted_rank": 49,
        "team_number": 49,
        "current_rank": 49,
        "current_rps": 49,
        "current_avg_rps": 84.4422,
    },
    # Subj Team
    {
        "driver_field_awareness": 84.4422,
        "driver_quickness": 84.4422,
        "driver_ability": 84.4422,
        "test_driver_ability": 84.4422,
        "unadjusted_field_awareness": 84.4422,
        "unadjusted_quickness": 84.4422,
        "team_number": 49,
    },
    # TBA Team
    {
        "team_name": "yyyyyyyyyyyyyyyyyyyyyy",
        "auto_line_successes": 49,
        "team_number": 49,
    },
    # TBA TIM
    {
        "auto_line": True,
        "match_number": 49,
        "team_number": 49,
    },
    # Obj Pit
    {
        "team_number": 49,
        "drivetrain": 1,
        "drivetrain_motor_type": 1,
        "drivetrain_motors": 49,
        "has_ground_intake": True,
        "can_eject_terminal": True,
        "has_vision": True,
        "can_cheesecake": True,
        "can_intake_terminal": True,
        "can_under_low_rung": True,
        "can_climb": True,
    },
]


class TestDataGenerator:
    def setup_method(self):
        self.input_filename = "schema/calc_obj_tim_schema.yml"
        self.generate_test_data = DataGenerator(self.input_filename)

        self.schema_files = utils.get_schema_filenames()
        self.schema_files = list(self.schema_files)
        self.schema_files.sort()

    def test_open_schema_file(self):
        schema = self.generate_test_data.open_schema_file(self.input_filename)
        assert utils.read_schema(self.input_filename) == schema

    def test_get_datapoint_collections_generation(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            datapoint_collections = generate_test_data.get_datapoint_collections_generation()
            assert "schema_file" not in datapoint_collections

    def test_generate_for_each_datapoint_collection(self):
        for num, schema_file in enumerate(self.schema_files):
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            generated_structure = generate_test_data.generate_for_each_datapoint_collection()
            assert generated_structure == CORRECT_SCHEMA_DATAPOINT_COLLECTIONS[num]

    def test_format_raw_data(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            formated_raw_data = generate_test_data.format_raw_data()
            assert isinstance(formated_raw_data, dict)
            assert "schema_file" not in formated_raw_data
            assert "data" not in formated_raw_data

    def test_request_single_data_struct(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            single_raw_data = generate_test_data.request_single_data_struct()
            assert isinstance(single_raw_data, dict)
            assert "schema_file" not in single_raw_data
            assert "data" not in single_raw_data

    def test_get_data(self):
        for schema_file in self.schema_files:
            generate_test_data = DataGenerator(f"schema/{schema_file}", seed=0)
            for num in range(5):
                list_of_raw_data_structures = generate_test_data.get_data(num)
                assert isinstance(list_of_raw_data_structures, list)
                assert len(list_of_raw_data_structures) == num


def test_name_sample_data():
    schema_files = utils.get_schema_filenames()
    schema_files = list(schema_files)
    schema_files.sort()

    for schema in schema_files:
        data = generate_test_data.name_sample_data(f"schema/{schema}", 1)
        assert isinstance(data, dict)
        assert isinstance(data[f"schema/{schema}"], dict)


def test_parse_args():
    sys.argv = [
        "generate_test_data.py",
        "-i",
        "schema/calc_predicted_aim_schema.yml",
        "-n",
        "2",
    ]
    parsed = parse_args()
    assert parsed.infile == sys.argv[2]
    assert parsed.number == sys.argv[4]
