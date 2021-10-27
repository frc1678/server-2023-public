import datetime

import pytest

import server
from calculations import decompressor


@pytest.mark.clouddb
class TestDecompressor:
    def setup_method(self, method):
        self.test_server = server.Server()
        self.test_decompressor = decompressor.Decompressor(self.test_server)

    def test___init__(self):
        assert self.test_decompressor.server == self.test_server
        assert self.test_decompressor.watched_collections == ['raw_qr']


    def test_convert_data_type(self):
        # List of compressed names and decompressed names of enums
        enum_dict = {
            'AA': 'score_ball_high',
            'AB': 'score_ball_low',
            'AC': 'start_incap',
            'AD': 'end_incap',
            'AE': 'control_panel_rotation',
            'AF': 'control_panel_position',
            'AG': 'start_climb',
            'AH': 'end_climb',
        }
        # Test a few values for each type to make sure they make sense
        assert 5 == self.test_decompressor.convert_data_type('5', 'int')
        assert 6 == self.test_decompressor.convert_data_type(6.43, 'int')
        assert 5.0 == self.test_decompressor.convert_data_type('5', 'float')
        assert 6.32 == self.test_decompressor.convert_data_type('6.32', 'float')
        assert 3.0 == self.test_decompressor.convert_data_type(3, 'float')
        assert self.test_decompressor.convert_data_type('1', 'bool')
        assert self.test_decompressor.convert_data_type('T', 'bool')
        assert self.test_decompressor.convert_data_type('TRUE', 'bool')
        assert not self.test_decompressor.convert_data_type('0', 'bool')
        assert not self.test_decompressor.convert_data_type('F', 'bool')
        assert not self.test_decompressor.convert_data_type('FALSE', 'bool')
        assert '' == self.test_decompressor.convert_data_type('', 'str')
        # Test all enums
        for compressed, decompressed in enum_dict.items():
            assert decompressed == self.test_decompressor.convert_data_type(
                compressed, 'Enum', name='action_type'
            )
        # Test error raising
        with pytest.raises(ValueError) as type_error:
            self.test_decompressor.convert_data_type('', 'tuple')
        assert 'Type tuple not recognized' in str(type_error.value)

    def test_get_decompressed_name(self):
        # Test for the that '$' returns '_separator' in all 3 sections that have it
        sections = ['generic_data', 'objective_tim', 'subjective_aim']
        for section in sections:
            assert '_separator' == self.test_decompressor.get_decompressed_name('$', section)
        # Test for a name with a string and a name with a list from each section
        assert '_section_separator' == self.test_decompressor.get_decompressed_name('%', 'generic_data')
        assert 'serial_number' == self.test_decompressor.get_decompressed_name('B', 'generic_data')
        assert 'timeline' == self.test_decompressor.get_decompressed_name('W', 'objective_tim')
        assert '_start_character' == self.test_decompressor.get_decompressed_name('+', 'objective_tim')
        assert 'time' == self.test_decompressor.get_decompressed_name(3, 'timeline')
        assert '_start_character' == self.test_decompressor.get_decompressed_name('*', 'subjective_aim')
        assert '_separator_internal' == self.test_decompressor.get_decompressed_name(':', 'subjective_aim')
        assert 'field_awareness_rankings' == self.test_decompressor.get_decompressed_name('B', 'subjective_aim')
        assert 'score_ball_high' == self.test_decompressor.get_decompressed_name('AA', 'action_type')
        assert 'end_climb' == self.test_decompressor.get_decompressed_name('AH', 'action_type')
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.get_decompressed_name('#', 'generic_data')
        assert 'Retrieving Variable Name # from generic_data failed.' in str(excinfo)

    def test_get_decompressed_type(self):
        # Test when there are two values in a list
        assert 'int' == self.test_decompressor.get_decompressed_type('schema_version', 'generic_data')
        assert 'str' == self.test_decompressor.get_decompressed_type('serial_number', 'generic_data')
        # Test when list has more than two values
        assert ['list', 'dict'] == self.test_decompressor.get_decompressed_type('timeline', 'objective_tim')

    def test_decompress_data(self):
        # Test generic data
        assert {'schema_version': 19, 'scout_name': 'Name'} == self.test_decompressor.decompress_data(
            ['A19', 'FName'], 'generic_data'
        )
        # Test objective tim
        assert {'team_number': 1678} == self.test_decompressor.decompress_data(['Z1678'], 'objective_tim')
        # Test timeline decompression
        assert {
                   'timeline': [{'action_type': 'score_ball_low', 'time': 51}]
               } == self.test_decompressor.decompress_data(['W051AB'], 'objective_tim')
        # Test using list with internal separators
        assert {'quickness_rankings': [1678, 1323, 254]} == self.test_decompressor.decompress_data(
            ['A1678:1323:254'], 'subjective_aim'
        )

    def test_decompress_generic_qr(self):
        # Test if the correct error is raised when the Schema version is incorrect
        with pytest.raises(LookupError) as version_error:
            self.test_decompressor.decompress_generic_qr('A14$')
        assert 'does not match Server version' in str(version_error)
        # What decompress_generic_qr() should return
        expected_decompressed_data = {
            'schema_version': 19,
            'serial_number': 's1234',
            'match_number': 34,
            'timestamp': 1230,
            'match_collection_version_number': 'v1.3',
            'scout_name': 'Name',
        }
        assert expected_decompressed_data == self.test_decompressor.decompress_generic_qr(
            'A19$Bs1234$C34$D1230$Ev1.3$FName'
        )


    def test_decompress_timeline(self):
        # Function should raise an error if the data isn't the right length
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_timeline(['abcdefg'])
        assert 'Invalid timeline -- Timeline length invalid: [\'abcdefg\']' in str(excinfo)
        # Test timeline decompression
        assert [
                   {'time': 60, 'action_type': 'start_climb'},
                   {'time': 61, 'action_type': 'end_climb'},
               ] == self.test_decompressor.decompress_timeline('060AG061AH')
        # Should return empty list if passed an empty string
        assert [] == self.test_decompressor.decompress_timeline('')

    def test_decompress_single_qr(self):
        # Expected decompressed objective qr
        expected_objective = {
            'schema_version': 19,
            'serial_number': 's1234',
            'match_number': 34,
            'timestamp': 1230,
            'match_collection_version_number': 'v1.3',
            'scout_name': 'Name',
            'team_number': 1678,
            'scout_id': 14,
            'timeline': [
                {'time': 60, 'action_type': 'start_climb'},
                {'time': 61, 'action_type': 'end_climb'},
            ],
        }
        # Expected decompressed subjective qr
        expected_subjective = {
            'schema_version': 19,
            'serial_number': 's1234',
            'match_number': 34,
            'timestamp': 1230,
            'match_collection_version_number': 'v1.3',
            'scout_name': 'Name',
            'quickness_rankings': [1678, 1323, 254],
            'field_awareness_rankings': [1323, 1678, 254],
        }
        # Test objective qr decompression
        assert expected_objective == self.test_decompressor.decompress_single_qr(
            'A19$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14$W060AG061AH', decompressor.QRType.OBJECTIVE
        )
        # Test subjective qr decompression
        assert expected_subjective == self.test_decompressor.decompress_single_qr(
            'A19$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254$B1323:1678:254',
            decompressor.QRType.SUBJECTIVE,
        )
        # Test error raising for objective and subjective using incomplete qrs
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                'A19$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14', decompressor.QRType.OBJECTIVE
            )
        assert 'QR missing data fields' in str(excinfo)
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                'A19$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254', decompressor.QRType.SUBJECTIVE
            )
        assert 'QR missing data fields' in str(excinfo)

    def test_decompress_qrs(self):
        # Expected output from a list containing one obj qr and one subj qr
        expected_output = {
            'unconsolidated_obj_tim': [
                {
                    'schema_version': 19,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1678,
                    'scout_id': 14,
                    'timeline': [
                        {'time': 60, 'action_type': 'start_climb'},
                        {'time': 61, 'action_type': 'end_climb'},
                    ],
                }
            ],
            'subj_aim': [
                {
                    'schema_version': 19,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'quickness_rankings': [1678, 1323, 254],
                    'field_awareness_rankings': [1323, 1678, 254],
                }
            ],
        }
        assert expected_output == self.test_decompressor.decompress_qrs(
            [
                {'data': '+A19$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14$W060AG061AH'},
                {'data': '*A19$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254$B1323:1678:254'},
            ]
        )

    def test_run(self):
        expected_obj = {
            "schema_version": 19,
            "serial_number": "gCbtwqZ",
            "match_number": 51,
            "timestamp": 932341,
            "match_collection_version_number": "v1.3",
            "scout_name": "XvfaPcSrgJw25VKrcsphdbyEVjmHrH1V",
            "team_number": 3603,
            "scout_id": 13,
            "timeline": [
                {
                    "time": 0,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 1,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 2,
                    "action_type": "end_climb"
                },
                {
                    "time": 3,
                    "action_type": "start_climb"
                },
                {
                    "time": 4,
                    "action_type": "start_climb"
                },
                {
                    "time": 5,
                    "action_type": "start_climb"
                },
                {
                    "time": 6,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 7,
                    "action_type": "end_climb"
                },
                {
                    "time": 8,
                    "action_type": "start_climb"
                },
                {
                    "time": 9,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 10,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 11,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 12,
                    "action_type": "start_incap"
                },
                {
                    "time": 13,
                    "action_type": "end_climb"
                },
                {
                    "time": 14,
                    "action_type": "start_incap"
                },
                {
                    "time": 15,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 16,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 17,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 18,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 19,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 20,
                    "action_type": "start_incap"
                },
                {
                    "time": 21,
                    "action_type": "start_incap"
                },
                {
                    "time": 22,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 23,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 24,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 25,
                    "action_type": "end_climb"
                },
                {
                    "time": 26,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 27,
                    "action_type": "end_incap"
                },
                {
                    "time": 28,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 29,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 30,
                    "action_type": "start_climb"
                },
                {
                    "time": 31,
                    "action_type": "end_incap"
                },
                {
                    "time": 32,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 33,
                    "action_type": "start_climb"
                },
                {
                    "time": 34,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 35,
                    "action_type": "end_climb"
                },
                {
                    "time": 36,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 37,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 38,
                    "action_type": "start_incap"
                },
                {
                    "time": 39,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 40,
                    "action_type": "start_climb"
                },
                {
                    "time": 41,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 42,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 43,
                    "action_type": "end_climb"
                },
                {
                    "time": 44,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 45,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 46,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 47,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 48,
                    "action_type": "end_climb"
                },
                {
                    "time": 49,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 50,
                    "action_type": "start_climb"
                },
                {
                    "time": 51,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 52,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 53,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 54,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 55,
                    "action_type": "end_incap"
                },
                {
                    "time": 56,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 57,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 58,
                    "action_type": "start_incap"
                },
                {
                    "time": 59,
                    "action_type": "start_climb"
                },
                {
                    "time": 60,
                    "action_type": "end_climb"
                },
                {
                    "time": 61,
                    "action_type": "start_climb"
                },
                {
                    "time": 62,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 63,
                    "action_type": "start_climb"
                },
                {
                    "time": 64,
                    "action_type": "end_incap"
                },
                {
                    "time": 65,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 66,
                    "action_type": "start_incap"
                },
                {
                    "time": 67,
                    "action_type": "start_climb"
                },
                {
                    "time": 68,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 69,
                    "action_type": "end_climb"
                },
                {
                    "time": 70,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 71,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 72,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 73,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 74,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 75,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 76,
                    "action_type": "start_climb"
                },
                {
                    "time": 77,
                    "action_type": "start_incap"
                },
                {
                    "time": 78,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 79,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 80,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 81,
                    "action_type": "end_incap"
                },
                {
                    "time": 82,
                    "action_type": "end_incap"
                },
                {
                    "time": 83,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 84,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 85,
                    "action_type": "end_incap"
                },
                {
                    "time": 86,
                    "action_type": "start_climb"
                },
                {
                    "time": 87,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 88,
                    "action_type": "end_incap"
                },
                {
                    "time": 89,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 90,
                    "action_type": "start_climb"
                },
                {
                    "time": 91,
                    "action_type": "start_climb"
                },
                {
                    "time": 92,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 93,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 94,
                    "action_type": "start_incap"
                },
                {
                    "time": 95,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 96,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 97,
                    "action_type": "start_climb"
                },
                {
                    "time": 98,
                    "action_type": "start_climb"
                },
                {
                    "time": 99,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 100,
                    "action_type": "end_incap"
                },
                {
                    "time": 101,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 102,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 103,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 104,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 105,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 106,
                    "action_type": "end_climb"
                },
                {
                    "time": 107,
                    "action_type": "start_incap"
                },
                {
                    "time": 108,
                    "action_type": "end_climb"
                },
                {
                    "time": 109,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 110,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 111,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 112,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 113,
                    "action_type": "start_climb"
                },
                {
                    "time": 114,
                    "action_type": "start_incap"
                },
                {
                    "time": 115,
                    "action_type": "start_incap"
                },
                {
                    "time": 116,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 117,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 118,
                    "action_type": "end_incap"
                },
                {
                    "time": 119,
                    "action_type": "end_incap"
                },
                {
                    "time": 120,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 121,
                    "action_type": "start_incap"
                },
                {
                    "time": 122,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 123,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 124,
                    "action_type": "start_incap"
                },
                {
                    "time": 125,
                    "action_type": "start_climb"
                },
                {
                    "time": 126,
                    "action_type": "end_incap"
                },
                {
                    "time": 127,
                    "action_type": "end_incap"
                },
                {
                    "time": 128,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 129,
                    "action_type": "start_climb"
                },
                {
                    "time": 130,
                    "action_type": "start_incap"
                },
                {
                    "time": 131,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 132,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 133,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 134,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 135,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 136,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 137,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 138,
                    "action_type": "start_climb"
                },
                {
                    "time": 139,
                    "action_type": "end_climb"
                },
                {
                    "time": 140,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 141,
                    "action_type": "start_climb"
                },
                {
                    "time": 142,
                    "action_type": "end_climb"
                },
                {
                    "time": 143,
                    "action_type": "end_climb"
                },
                {
                    "time": 144,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 145,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 146,
                    "action_type": "start_climb"
                },
                {
                    "time": 147,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 148,
                    "action_type": "start_incap"
                },
                {
                    "time": 149,
                    "action_type": "end_climb"
                },
                {
                    "time": 150,
                    "action_type": "start_incap"
                },
                {
                    "time": 151,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 152,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 153,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 154,
                    "action_type": "start_climb"
                },
                {
                    "time": 155,
                    "action_type": "end_climb"
                },
                {
                    "time": 156,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 157,
                    "action_type": "start_climb"
                },
                {
                    "time": 158,
                    "action_type": "end_incap"
                },
                {
                    "time": 159,
                    "action_type": "end_climb"
                },
                {
                    "time": 160,
                    "action_type": "end_climb"
                },
                {
                    "time": 161,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 162,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 163,
                    "action_type": "start_incap"
                },
                {
                    "time": 164,
                    "action_type": "end_climb"
                },
                {
                    "time": 165,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 166,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 167,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 168,
                    "action_type": "start_incap"
                },
                {
                    "time": 169,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 170,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 171,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 172,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 173,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 174,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 175,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 176,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 177,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 178,
                    "action_type": "end_incap"
                },
                {
                    "time": 179,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 180,
                    "action_type": "start_incap"
                },
                {
                    "time": 181,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 182,
                    "action_type": "start_incap"
                },
                {
                    "time": 183,
                    "action_type": "start_climb"
                },
                {
                    "time": 184,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 185,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 186,
                    "action_type": "end_climb"
                },
                {
                    "time": 187,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 188,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 189,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 190,
                    "action_type": "start_incap"
                },
                {
                    "time": 191,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 192,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 193,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 194,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 195,
                    "action_type": "start_incap"
                },
                {
                    "time": 196,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 197,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 198,
                    "action_type": "end_incap"
                },
                {
                    "time": 199,
                    "action_type": "end_climb"
                },
                {
                    "time": 200,
                    "action_type": "end_climb"
                },
                {
                    "time": 201,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 202,
                    "action_type": "end_incap"
                },
                {
                    "time": 203,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 204,
                    "action_type": "start_climb"
                },
                {
                    "time": 205,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 206,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 207,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 208,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 209,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 210,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 211,
                    "action_type": "start_climb"
                },
                {
                    "time": 212,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 213,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 214,
                    "action_type": "end_incap"
                },
                {
                    "time": 215,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 216,
                    "action_type": "start_climb"
                },
                {
                    "time": 217,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 218,
                    "action_type": "start_climb"
                },
                {
                    "time": 219,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 220,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 221,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 222,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 223,
                    "action_type": "start_climb"
                },
                {
                    "time": 224,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 225,
                    "action_type": "start_climb"
                },
                {
                    "time": 226,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 227,
                    "action_type": "start_incap"
                },
                {
                    "time": 228,
                    "action_type": "end_climb"
                },
                {
                    "time": 229,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 230,
                    "action_type": "end_climb"
                },
                {
                    "time": 231,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 232,
                    "action_type": "end_climb"
                },
                {
                    "time": 233,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 234,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 235,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 236,
                    "action_type": "start_climb"
                },
                {
                    "time": 237,
                    "action_type": "start_climb"
                },
                {
                    "time": 238,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 239,
                    "action_type": "end_incap"
                },
                {
                    "time": 240,
                    "action_type": "end_incap"
                },
                {
                    "time": 241,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 242,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 243,
                    "action_type": "end_climb"
                },
                {
                    "time": 244,
                    "action_type": "end_climb"
                },
                {
                    "time": 245,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 246,
                    "action_type": "start_incap"
                },
                {
                    "time": 247,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 248,
                    "action_type": "end_incap"
                },
                {
                    "time": 249,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 250,
                    "action_type": "start_climb"
                },
                {
                    "time": 251,
                    "action_type": "end_climb"
                },
                {
                    "time": 252,
                    "action_type": "end_climb"
                },
                {
                    "time": 253,
                    "action_type": "end_incap"
                },
                {
                    "time": 254,
                    "action_type": "start_incap"
                },
                {
                    "time": 255,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 256,
                    "action_type": "start_climb"
                },
                {
                    "time": 257,
                    "action_type": "start_climb"
                },
                {
                    "time": 258,
                    "action_type": "start_climb"
                },
                {
                    "time": 259,
                    "action_type": "start_incap"
                },
                {
                    "time": 260,
                    "action_type": "start_incap"
                },
                {
                    "time": 261,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 262,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 263,
                    "action_type": "start_climb"
                },
                {
                    "time": 264,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 265,
                    "action_type": "start_climb"
                },
                {
                    "time": 266,
                    "action_type": "end_climb"
                },
                {
                    "time": 267,
                    "action_type": "end_incap"
                },
                {
                    "time": 268,
                    "action_type": "start_climb"
                },
                {
                    "time": 269,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 270,
                    "action_type": "end_climb"
                },
                {
                    "time": 271,
                    "action_type": "end_incap"
                },
                {
                    "time": 272,
                    "action_type": "end_climb"
                },
                {
                    "time": 273,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 274,
                    "action_type": "start_climb"
                },
                {
                    "time": 275,
                    "action_type": "start_climb"
                },
                {
                    "time": 276,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 277,
                    "action_type": "end_incap"
                },
                {
                    "time": 278,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 279,
                    "action_type": "end_climb"
                },
                {
                    "time": 280,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 281,
                    "action_type": "start_climb"
                },
                {
                    "time": 282,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 283,
                    "action_type": "start_climb"
                },
                {
                    "time": 284,
                    "action_type": "start_incap"
                },
                {
                    "time": 285,
                    "action_type": "end_climb"
                },
                {
                    "time": 286,
                    "action_type": "start_climb"
                },
                {
                    "time": 287,
                    "action_type": "end_incap"
                },
                {
                    "time": 288,
                    "action_type": "start_climb"
                },
                {
                    "time": 289,
                    "action_type": "start_incap"
                },
                {
                    "time": 290,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 291,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 292,
                    "action_type": "end_climb"
                },
                {
                    "time": 293,
                    "action_type": "start_incap"
                },
                {
                    "time": 294,
                    "action_type": "start_incap"
                },
                {
                    "time": 295,
                    "action_type": "start_climb"
                },
                {
                    "time": 296,
                    "action_type": "end_incap"
                },
                {
                    "time": 297,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 298,
                    "action_type": "start_climb"
                },
                {
                    "time": 299,
                    "action_type": "end_incap"
                },
                {
                    "time": 300,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 301,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 302,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 303,
                    "action_type": "start_climb"
                },
                {
                    "time": 304,
                    "action_type": "start_incap"
                },
                {
                    "time": 305,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 306,
                    "action_type": "start_incap"
                },
                {
                    "time": 307,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 308,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 309,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 310,
                    "action_type": "start_incap"
                },
                {
                    "time": 311,
                    "action_type": "start_climb"
                },
                {
                    "time": 312,
                    "action_type": "end_incap"
                },
                {
                    "time": 313,
                    "action_type": "start_climb"
                },
                {
                    "time": 314,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 315,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 316,
                    "action_type": "start_climb"
                },
                {
                    "time": 317,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 318,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 319,
                    "action_type": "end_climb"
                },
                {
                    "time": 320,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 321,
                    "action_type": "start_incap"
                },
                {
                    "time": 322,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 323,
                    "action_type": "end_incap"
                },
                {
                    "time": 324,
                    "action_type": "end_incap"
                },
                {
                    "time": 325,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 326,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 327,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 328,
                    "action_type": "start_incap"
                },
                {
                    "time": 329,
                    "action_type": "start_climb"
                },
                {
                    "time": 330,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 331,
                    "action_type": "end_incap"
                },
                {
                    "time": 332,
                    "action_type": "end_climb"
                },
                {
                    "time": 333,
                    "action_type": "start_incap"
                },
                {
                    "time": 334,
                    "action_type": "start_incap"
                },
                {
                    "time": 335,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 336,
                    "action_type": "end_climb"
                },
                {
                    "time": 337,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 338,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 339,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 340,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 341,
                    "action_type": "end_incap"
                },
                {
                    "time": 342,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 343,
                    "action_type": "start_climb"
                },
                {
                    "time": 344,
                    "action_type": "end_climb"
                },
                {
                    "time": 345,
                    "action_type": "end_incap"
                },
                {
                    "time": 346,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 347,
                    "action_type": "end_climb"
                },
                {
                    "time": 348,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 349,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 350,
                    "action_type": "end_climb"
                },
                {
                    "time": 351,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 352,
                    "action_type": "start_climb"
                },
                {
                    "time": 353,
                    "action_type": "end_incap"
                },
                {
                    "time": 354,
                    "action_type": "start_incap"
                },
                {
                    "time": 355,
                    "action_type": "start_climb"
                },
                {
                    "time": 356,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 357,
                    "action_type": "end_climb"
                },
                {
                    "time": 358,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 359,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 360,
                    "action_type": "start_incap"
                },
                {
                    "time": 361,
                    "action_type": "end_climb"
                },
                {
                    "time": 362,
                    "action_type": "end_incap"
                },
                {
                    "time": 363,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 364,
                    "action_type": "end_incap"
                },
                {
                    "time": 365,
                    "action_type": "end_incap"
                },
                {
                    "time": 366,
                    "action_type": "start_climb"
                },
                {
                    "time": 367,
                    "action_type": "start_climb"
                },
                {
                    "time": 368,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 369,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 370,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 371,
                    "action_type": "start_incap"
                },
                {
                    "time": 372,
                    "action_type": "start_climb"
                },
                {
                    "time": 373,
                    "action_type": "end_incap"
                },
                {
                    "time": 374,
                    "action_type": "end_incap"
                },
                {
                    "time": 375,
                    "action_type": "end_climb"
                },
                {
                    "time": 376,
                    "action_type": "end_incap"
                },
                {
                    "time": 377,
                    "action_type": "start_climb"
                },
                {
                    "time": 378,
                    "action_type": "start_incap"
                },
                {
                    "time": 379,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 380,
                    "action_type": "end_incap"
                },
                {
                    "time": 381,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 382,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 383,
                    "action_type": "start_climb"
                },
                {
                    "time": 384,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 385,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 386,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 387,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 388,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 389,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 390,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 391,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 392,
                    "action_type": "end_incap"
                },
                {
                    "time": 393,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 394,
                    "action_type": "start_incap"
                },
                {
                    "time": 395,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 396,
                    "action_type": "end_climb"
                },
                {
                    "time": 397,
                    "action_type": "end_climb"
                },
                {
                    "time": 398,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 399,
                    "action_type": "start_incap"
                },
                {
                    "time": 400,
                    "action_type": "start_incap"
                },
                {
                    "time": 401,
                    "action_type": "end_climb"
                },
                {
                    "time": 402,
                    "action_type": "start_incap"
                },
                {
                    "time": 403,
                    "action_type": "end_incap"
                },
                {
                    "time": 404,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 405,
                    "action_type": "end_climb"
                },
                {
                    "time": 406,
                    "action_type": "start_climb"
                },
                {
                    "time": 407,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 408,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 409,
                    "action_type": "end_climb"
                },
                {
                    "time": 410,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 411,
                    "action_type": "start_climb"
                },
                {
                    "time": 412,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 413,
                    "action_type": "start_climb"
                },
                {
                    "time": 414,
                    "action_type": "start_incap"
                },
                {
                    "time": 415,
                    "action_type": "end_climb"
                },
                {
                    "time": 416,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 417,
                    "action_type": "start_climb"
                },
                {
                    "time": 418,
                    "action_type": "end_incap"
                },
                {
                    "time": 419,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 420,
                    "action_type": "end_climb"
                },
                {
                    "time": 421,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 422,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 423,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 424,
                    "action_type": "start_incap"
                },
                {
                    "time": 425,
                    "action_type": "end_climb"
                },
                {
                    "time": 426,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 427,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 428,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 429,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 430,
                    "action_type": "end_climb"
                },
                {
                    "time": 431,
                    "action_type": "end_climb"
                },
                {
                    "time": 432,
                    "action_type": "start_climb"
                },
                {
                    "time": 433,
                    "action_type": "start_climb"
                },
                {
                    "time": 434,
                    "action_type": "end_climb"
                },
                {
                    "time": 435,
                    "action_type": "end_incap"
                },
                {
                    "time": 436,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 437,
                    "action_type": "start_incap"
                },
                {
                    "time": 438,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 439,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 440,
                    "action_type": "end_climb"
                },
                {
                    "time": 441,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 442,
                    "action_type": "end_climb"
                },
                {
                    "time": 443,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 444,
                    "action_type": "start_incap"
                },
                {
                    "time": 445,
                    "action_type": "start_incap"
                },
                {
                    "time": 446,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 447,
                    "action_type": "start_climb"
                },
                {
                    "time": 448,
                    "action_type": "start_incap"
                },
                {
                    "time": 449,
                    "action_type": "end_climb"
                },
                {
                    "time": 450,
                    "action_type": "end_climb"
                },
                {
                    "time": 451,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 452,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 453,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 454,
                    "action_type": "start_incap"
                },
                {
                    "time": 455,
                    "action_type": "end_incap"
                },
                {
                    "time": 456,
                    "action_type": "end_incap"
                },
                {
                    "time": 457,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 458,
                    "action_type": "start_incap"
                },
                {
                    "time": 459,
                    "action_type": "end_climb"
                },
                {
                    "time": 460,
                    "action_type": "start_incap"
                },
                {
                    "time": 461,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 462,
                    "action_type": "end_climb"
                },
                {
                    "time": 463,
                    "action_type": "end_incap"
                },
                {
                    "time": 464,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 465,
                    "action_type": "end_climb"
                },
                {
                    "time": 466,
                    "action_type": "start_incap"
                },
                {
                    "time": 467,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 468,
                    "action_type": "start_incap"
                },
                {
                    "time": 469,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 470,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 471,
                    "action_type": "start_incap"
                },
                {
                    "time": 472,
                    "action_type": "start_climb"
                },
                {
                    "time": 473,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 474,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 475,
                    "action_type": "start_incap"
                },
                {
                    "time": 476,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 477,
                    "action_type": "start_incap"
                },
                {
                    "time": 478,
                    "action_type": "start_climb"
                },
                {
                    "time": 479,
                    "action_type": "start_incap"
                },
                {
                    "time": 480,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 481,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 482,
                    "action_type": "start_climb"
                },
                {
                    "time": 483,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 484,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 485,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 486,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 487,
                    "action_type": "end_climb"
                },
                {
                    "time": 488,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 489,
                    "action_type": "end_climb"
                },
                {
                    "time": 490,
                    "action_type": "start_climb"
                },
                {
                    "time": 491,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 492,
                    "action_type": "start_incap"
                },
                {
                    "time": 493,
                    "action_type": "end_climb"
                },
                {
                    "time": 494,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 495,
                    "action_type": "end_incap"
                },
                {
                    "time": 496,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 497,
                    "action_type": "end_incap"
                },
                {
                    "time": 498,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 499,
                    "action_type": "end_incap"
                },
                {
                    "time": 500,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 501,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 502,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 503,
                    "action_type": "end_climb"
                },
                {
                    "time": 504,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 505,
                    "action_type": "start_incap"
                },
                {
                    "time": 506,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 507,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 508,
                    "action_type": "start_climb"
                },
                {
                    "time": 509,
                    "action_type": "start_incap"
                },
                {
                    "time": 510,
                    "action_type": "end_climb"
                },
                {
                    "time": 511,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 512,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 513,
                    "action_type": "end_climb"
                },
                {
                    "time": 514,
                    "action_type": "start_incap"
                },
                {
                    "time": 515,
                    "action_type": "start_climb"
                },
                {
                    "time": 516,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 517,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 518,
                    "action_type": "end_incap"
                },
                {
                    "time": 519,
                    "action_type": "end_incap"
                },
                {
                    "time": 520,
                    "action_type": "start_incap"
                },
                {
                    "time": 521,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 522,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 523,
                    "action_type": "start_incap"
                },
                {
                    "time": 524,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 525,
                    "action_type": "end_climb"
                },
                {
                    "time": 526,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 527,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 528,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 529,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 530,
                    "action_type": "end_climb"
                },
                {
                    "time": 531,
                    "action_type": "end_climb"
                },
                {
                    "time": 532,
                    "action_type": "start_climb"
                },
                {
                    "time": 533,
                    "action_type": "end_incap"
                },
                {
                    "time": 534,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 535,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 536,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 537,
                    "action_type": "end_incap"
                },
                {
                    "time": 538,
                    "action_type": "start_climb"
                },
                {
                    "time": 539,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 540,
                    "action_type": "start_climb"
                },
                {
                    "time": 541,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 542,
                    "action_type": "end_incap"
                },
                {
                    "time": 543,
                    "action_type": "end_incap"
                },
                {
                    "time": 544,
                    "action_type": "start_incap"
                },
                {
                    "time": 545,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 546,
                    "action_type": "end_incap"
                },
                {
                    "time": 547,
                    "action_type": "end_climb"
                },
                {
                    "time": 548,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 549,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 550,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 551,
                    "action_type": "start_incap"
                },
                {
                    "time": 552,
                    "action_type": "end_climb"
                },
                {
                    "time": 553,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 554,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 555,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 556,
                    "action_type": "end_incap"
                },
                {
                    "time": 557,
                    "action_type": "start_climb"
                },
                {
                    "time": 558,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 559,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 560,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 561,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 562,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 563,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 564,
                    "action_type": "start_climb"
                },
                {
                    "time": 565,
                    "action_type": "start_incap"
                },
                {
                    "time": 566,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 567,
                    "action_type": "start_incap"
                },
                {
                    "time": 568,
                    "action_type": "start_climb"
                },
                {
                    "time": 569,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 570,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 571,
                    "action_type": "start_climb"
                },
                {
                    "time": 572,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 573,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 574,
                    "action_type": "end_climb"
                },
                {
                    "time": 575,
                    "action_type": "end_incap"
                },
                {
                    "time": 576,
                    "action_type": "end_incap"
                },
                {
                    "time": 577,
                    "action_type": "end_incap"
                },
                {
                    "time": 578,
                    "action_type": "start_incap"
                },
                {
                    "time": 579,
                    "action_type": "start_incap"
                },
                {
                    "time": 580,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 581,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 582,
                    "action_type": "start_climb"
                },
                {
                    "time": 583,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 584,
                    "action_type": "start_climb"
                },
                {
                    "time": 585,
                    "action_type": "start_incap"
                },
                {
                    "time": 586,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 587,
                    "action_type": "end_incap"
                },
                {
                    "time": 588,
                    "action_type": "end_climb"
                },
                {
                    "time": 589,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 590,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 591,
                    "action_type": "end_climb"
                },
                {
                    "time": 592,
                    "action_type": "start_incap"
                },
                {
                    "time": 593,
                    "action_type": "end_climb"
                },
                {
                    "time": 594,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 595,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 596,
                    "action_type": "start_climb"
                },
                {
                    "time": 597,
                    "action_type": "end_climb"
                },
                {
                    "time": 598,
                    "action_type": "start_incap"
                },
                {
                    "time": 599,
                    "action_type": "start_climb"
                },
                {
                    "time": 600,
                    "action_type": "end_incap"
                },
                {
                    "time": 601,
                    "action_type": "start_incap"
                },
                {
                    "time": 602,
                    "action_type": "end_incap"
                },
                {
                    "time": 603,
                    "action_type": "start_climb"
                },
                {
                    "time": 604,
                    "action_type": "end_incap"
                },
                {
                    "time": 605,
                    "action_type": "end_climb"
                },
                {
                    "time": 606,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 607,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 608,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 609,
                    "action_type": "start_climb"
                },
                {
                    "time": 610,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 611,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 612,
                    "action_type": "start_climb"
                },
                {
                    "time": 613,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 614,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 615,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 616,
                    "action_type": "start_climb"
                },
                {
                    "time": 617,
                    "action_type": "end_incap"
                },
                {
                    "time": 618,
                    "action_type": "start_climb"
                },
                {
                    "time": 619,
                    "action_type": "start_incap"
                },
                {
                    "time": 620,
                    "action_type": "start_climb"
                },
                {
                    "time": 621,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 622,
                    "action_type": "start_climb"
                },
                {
                    "time": 623,
                    "action_type": "start_incap"
                },
                {
                    "time": 624,
                    "action_type": "end_climb"
                },
                {
                    "time": 625,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 626,
                    "action_type": "end_incap"
                },
                {
                    "time": 627,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 628,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 629,
                    "action_type": "start_incap"
                },
                {
                    "time": 630,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 631,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 632,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 633,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 634,
                    "action_type": "start_climb"
                },
                {
                    "time": 635,
                    "action_type": "end_climb"
                },
                {
                    "time": 636,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 637,
                    "action_type": "end_incap"
                },
                {
                    "time": 638,
                    "action_type": "end_incap"
                },
                {
                    "time": 639,
                    "action_type": "end_climb"
                },
                {
                    "time": 640,
                    "action_type": "end_climb"
                },
                {
                    "time": 641,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 642,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 643,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 644,
                    "action_type": "start_climb"
                },
                {
                    "time": 645,
                    "action_type": "end_incap"
                },
                {
                    "time": 646,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 647,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 648,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 649,
                    "action_type": "end_climb"
                },
                {
                    "time": 650,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 651,
                    "action_type": "end_incap"
                },
                {
                    "time": 652,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 653,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 654,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 655,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 656,
                    "action_type": "start_climb"
                },
                {
                    "time": 657,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 658,
                    "action_type": "start_climb"
                },
                {
                    "time": 659,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 660,
                    "action_type": "start_climb"
                },
                {
                    "time": 661,
                    "action_type": "start_climb"
                },
                {
                    "time": 662,
                    "action_type": "end_incap"
                },
                {
                    "time": 663,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 664,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 665,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 666,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 667,
                    "action_type": "start_incap"
                },
                {
                    "time": 668,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 669,
                    "action_type": "start_climb"
                },
                {
                    "time": 670,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 671,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 672,
                    "action_type": "end_incap"
                },
                {
                    "time": 673,
                    "action_type": "start_climb"
                },
                {
                    "time": 674,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 675,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 676,
                    "action_type": "start_climb"
                },
                {
                    "time": 677,
                    "action_type": "end_incap"
                },
                {
                    "time": 678,
                    "action_type": "end_climb"
                },
                {
                    "time": 679,
                    "action_type": "end_incap"
                },
                {
                    "time": 680,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 681,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 682,
                    "action_type": "end_incap"
                },
                {
                    "time": 683,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 684,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 685,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 686,
                    "action_type": "end_climb"
                },
                {
                    "time": 687,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 688,
                    "action_type": "end_incap"
                },
                {
                    "time": 689,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 690,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 691,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 692,
                    "action_type": "end_incap"
                },
                {
                    "time": 693,
                    "action_type": "start_climb"
                },
                {
                    "time": 694,
                    "action_type": "start_climb"
                },
                {
                    "time": 695,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 696,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 697,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 698,
                    "action_type": "start_climb"
                },
                {
                    "time": 699,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 700,
                    "action_type": "end_climb"
                },
                {
                    "time": 701,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 702,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 703,
                    "action_type": "end_climb"
                },
                {
                    "time": 704,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 705,
                    "action_type": "end_incap"
                },
                {
                    "time": 706,
                    "action_type": "end_incap"
                },
                {
                    "time": 707,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 708,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 709,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 710,
                    "action_type": "start_incap"
                },
                {
                    "time": 711,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 712,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 713,
                    "action_type": "end_climb"
                },
                {
                    "time": 714,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 715,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 716,
                    "action_type": "start_climb"
                },
                {
                    "time": 717,
                    "action_type": "end_climb"
                },
                {
                    "time": 718,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 719,
                    "action_type": "start_incap"
                },
                {
                    "time": 720,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 721,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 722,
                    "action_type": "end_incap"
                },
                {
                    "time": 723,
                    "action_type": "end_incap"
                },
                {
                    "time": 724,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 725,
                    "action_type": "end_climb"
                },
                {
                    "time": 726,
                    "action_type": "end_incap"
                },
                {
                    "time": 727,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 728,
                    "action_type": "end_climb"
                },
                {
                    "time": 729,
                    "action_type": "end_incap"
                },
                {
                    "time": 730,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 731,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 732,
                    "action_type": "end_incap"
                },
                {
                    "time": 733,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 734,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 735,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 736,
                    "action_type": "start_incap"
                },
                {
                    "time": 737,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 738,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 739,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 740,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 741,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 742,
                    "action_type": "start_climb"
                },
                {
                    "time": 743,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 744,
                    "action_type": "end_climb"
                },
                {
                    "time": 745,
                    "action_type": "end_climb"
                },
                {
                    "time": 746,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 747,
                    "action_type": "end_incap"
                },
                {
                    "time": 748,
                    "action_type": "end_incap"
                },
                {
                    "time": 749,
                    "action_type": "start_climb"
                },
                {
                    "time": 750,
                    "action_type": "end_incap"
                },
                {
                    "time": 751,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 752,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 753,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 754,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 755,
                    "action_type": "end_incap"
                },
                {
                    "time": 756,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 757,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 758,
                    "action_type": "start_climb"
                },
                {
                    "time": 759,
                    "action_type": "end_incap"
                },
                {
                    "time": 760,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 761,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 762,
                    "action_type": "start_incap"
                },
                {
                    "time": 763,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 764,
                    "action_type": "end_incap"
                },
                {
                    "time": 765,
                    "action_type": "end_climb"
                },
                {
                    "time": 766,
                    "action_type": "start_climb"
                },
                {
                    "time": 767,
                    "action_type": "start_climb"
                },
                {
                    "time": 768,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 769,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 770,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 771,
                    "action_type": "end_climb"
                },
                {
                    "time": 772,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 773,
                    "action_type": "start_incap"
                },
                {
                    "time": 774,
                    "action_type": "start_climb"
                },
                {
                    "time": 775,
                    "action_type": "end_incap"
                },
                {
                    "time": 776,
                    "action_type": "start_climb"
                },
                {
                    "time": 777,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 778,
                    "action_type": "end_climb"
                },
                {
                    "time": 779,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 780,
                    "action_type": "end_incap"
                },
                {
                    "time": 781,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 782,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 783,
                    "action_type": "end_incap"
                },
                {
                    "time": 784,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 785,
                    "action_type": "start_incap"
                },
                {
                    "time": 786,
                    "action_type": "end_climb"
                },
                {
                    "time": 787,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 788,
                    "action_type": "start_incap"
                },
                {
                    "time": 789,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 790,
                    "action_type": "start_incap"
                },
                {
                    "time": 791,
                    "action_type": "start_climb"
                },
                {
                    "time": 792,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 793,
                    "action_type": "start_climb"
                },
                {
                    "time": 794,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 795,
                    "action_type": "end_incap"
                },
                {
                    "time": 796,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 797,
                    "action_type": "start_incap"
                },
                {
                    "time": 798,
                    "action_type": "start_climb"
                },
                {
                    "time": 799,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 800,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 801,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 802,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 803,
                    "action_type": "end_climb"
                },
                {
                    "time": 804,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 805,
                    "action_type": "start_climb"
                },
                {
                    "time": 806,
                    "action_type": "end_incap"
                },
                {
                    "time": 807,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 808,
                    "action_type": "end_incap"
                },
                {
                    "time": 809,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 810,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 811,
                    "action_type": "end_incap"
                },
                {
                    "time": 812,
                    "action_type": "end_climb"
                },
                {
                    "time": 813,
                    "action_type": "start_incap"
                },
                {
                    "time": 814,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 815,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 816,
                    "action_type": "end_incap"
                },
                {
                    "time": 817,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 818,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 819,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 820,
                    "action_type": "end_incap"
                },
                {
                    "time": 821,
                    "action_type": "end_incap"
                },
                {
                    "time": 822,
                    "action_type": "end_incap"
                },
                {
                    "time": 823,
                    "action_type": "start_climb"
                },
                {
                    "time": 824,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 825,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 826,
                    "action_type": "start_incap"
                },
                {
                    "time": 827,
                    "action_type": "end_incap"
                },
                {
                    "time": 828,
                    "action_type": "end_incap"
                },
                {
                    "time": 829,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 830,
                    "action_type": "start_climb"
                },
                {
                    "time": 831,
                    "action_type": "start_climb"
                },
                {
                    "time": 832,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 833,
                    "action_type": "end_incap"
                },
                {
                    "time": 834,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 835,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 836,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 837,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 838,
                    "action_type": "start_climb"
                },
                {
                    "time": 839,
                    "action_type": "end_incap"
                },
                {
                    "time": 840,
                    "action_type": "start_climb"
                },
                {
                    "time": 841,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 842,
                    "action_type": "end_incap"
                },
                {
                    "time": 843,
                    "action_type": "start_climb"
                },
                {
                    "time": 844,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 845,
                    "action_type": "end_climb"
                },
                {
                    "time": 846,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 847,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 848,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 849,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 850,
                    "action_type": "end_climb"
                },
                {
                    "time": 851,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 852,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 853,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 854,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 855,
                    "action_type": "end_incap"
                },
                {
                    "time": 856,
                    "action_type": "start_incap"
                },
                {
                    "time": 857,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 858,
                    "action_type": "end_climb"
                },
                {
                    "time": 859,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 860,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 861,
                    "action_type": "start_incap"
                },
                {
                    "time": 862,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 863,
                    "action_type": "end_climb"
                },
                {
                    "time": 864,
                    "action_type": "start_incap"
                },
                {
                    "time": 865,
                    "action_type": "start_climb"
                },
                {
                    "time": 866,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 867,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 868,
                    "action_type": "end_incap"
                },
                {
                    "time": 869,
                    "action_type": "end_incap"
                },
                {
                    "time": 870,
                    "action_type": "end_climb"
                },
                {
                    "time": 871,
                    "action_type": "start_climb"
                },
                {
                    "time": 872,
                    "action_type": "end_climb"
                },
                {
                    "time": 873,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 874,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 875,
                    "action_type": "start_incap"
                },
                {
                    "time": 876,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 877,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 878,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 879,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 880,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 881,
                    "action_type": "end_climb"
                },
                {
                    "time": 882,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 883,
                    "action_type": "end_incap"
                },
                {
                    "time": 884,
                    "action_type": "end_incap"
                },
                {
                    "time": 885,
                    "action_type": "end_climb"
                },
                {
                    "time": 886,
                    "action_type": "end_climb"
                },
                {
                    "time": 887,
                    "action_type": "start_incap"
                },
                {
                    "time": 888,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 889,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 890,
                    "action_type": "start_climb"
                },
                {
                    "time": 891,
                    "action_type": "start_incap"
                },
                {
                    "time": 892,
                    "action_type": "end_incap"
                },
                {
                    "time": 893,
                    "action_type": "start_incap"
                },
                {
                    "time": 894,
                    "action_type": "end_incap"
                },
                {
                    "time": 895,
                    "action_type": "start_incap"
                },
                {
                    "time": 896,
                    "action_type": "start_incap"
                },
                {
                    "time": 897,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 898,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 899,
                    "action_type": "start_incap"
                },
                {
                    "time": 900,
                    "action_type": "start_incap"
                },
                {
                    "time": 901,
                    "action_type": "start_incap"
                },
                {
                    "time": 902,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 903,
                    "action_type": "start_climb"
                },
                {
                    "time": 904,
                    "action_type": "end_climb"
                },
                {
                    "time": 905,
                    "action_type": "start_climb"
                },
                {
                    "time": 906,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 907,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 908,
                    "action_type": "start_climb"
                },
                {
                    "time": 909,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 910,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 911,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 912,
                    "action_type": "start_incap"
                },
                {
                    "time": 913,
                    "action_type": "end_climb"
                },
                {
                    "time": 914,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 915,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 916,
                    "action_type": "start_climb"
                },
                {
                    "time": 917,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 918,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 919,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 920,
                    "action_type": "end_incap"
                },
                {
                    "time": 921,
                    "action_type": "end_incap"
                },
                {
                    "time": 922,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 923,
                    "action_type": "start_incap"
                },
                {
                    "time": 924,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 925,
                    "action_type": "end_incap"
                },
                {
                    "time": 926,
                    "action_type": "end_incap"
                },
                {
                    "time": 927,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 928,
                    "action_type": "end_climb"
                },
                {
                    "time": 929,
                    "action_type": "start_climb"
                },
                {
                    "time": 930,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 931,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 932,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 933,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 934,
                    "action_type": "start_climb"
                },
                {
                    "time": 935,
                    "action_type": "start_climb"
                },
                {
                    "time": 936,
                    "action_type": "end_incap"
                },
                {
                    "time": 937,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 938,
                    "action_type": "start_climb"
                },
                {
                    "time": 939,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 940,
                    "action_type": "end_climb"
                },
                {
                    "time": 941,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 942,
                    "action_type": "start_incap"
                },
                {
                    "time": 943,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 944,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 945,
                    "action_type": "start_climb"
                },
                {
                    "time": 946,
                    "action_type": "end_incap"
                },
                {
                    "time": 947,
                    "action_type": "end_incap"
                },
                {
                    "time": 948,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 949,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 950,
                    "action_type": "start_climb"
                },
                {
                    "time": 951,
                    "action_type": "end_climb"
                },
                {
                    "time": 952,
                    "action_type": "start_climb"
                },
                {
                    "time": 953,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 954,
                    "action_type": "start_climb"
                },
                {
                    "time": 955,
                    "action_type": "start_incap"
                },
                {
                    "time": 956,
                    "action_type": "end_climb"
                },
                {
                    "time": 957,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 958,
                    "action_type": "start_incap"
                },
                {
                    "time": 959,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 960,
                    "action_type": "start_climb"
                },
                {
                    "time": 961,
                    "action_type": "start_incap"
                },
                {
                    "time": 962,
                    "action_type": "start_incap"
                },
                {
                    "time": 963,
                    "action_type": "end_incap"
                },
                {
                    "time": 964,
                    "action_type": "start_incap"
                },
                {
                    "time": 965,
                    "action_type": "score_ball_high"
                },
                {
                    "time": 966,
                    "action_type": "start_climb"
                },
                {
                    "time": 967,
                    "action_type": "end_incap"
                },
                {
                    "time": 968,
                    "action_type": "control_panel_position"
                },
                {
                    "time": 969,
                    "action_type": "control_panel_rotation"
                },
                {
                    "time": 970,
                    "action_type": "score_ball_low"
                },
                {
                    "time": 971,
                    "action_type": "control_panel_position"
                }
            ]
        }
        expected_sbj = {
            "schema_version": 19,
            "serial_number": "Y",
            "match_number": 19,
            "timestamp": 23789,
            "match_collection_version_number": "v1.3",
            "scout_name": "oV5tmZ1oWu",
            "field_awareness_rankings": [
                304,
                7730,
                7582,
                8060,
                506,
                7178,
                2076,
                8471,
                1809,
                3746,
                5738,
                3741,
                2095,
                1962,
                4544,
                1084,
                8282,
                1648,
                9409,
                8256,
                6514,
                1284,
                9998
            ],
            "quickness_rankings": [
                8282,
                506,
                5738,
                8256,
                7582,
                9409,
                3741,
                304,
                1809,
                7730,
                4544,
                1962,
                6514,
                3746,
                8060,
                2076,
                1284,
                1648,
                7178,
                2095,
                1084,
                8471,
                9998
            ]
        }
        curr_time = datetime.datetime.utcnow()

        self.test_server.db.insert_documents('raw_qr', [
            {
                'data': '+A19$BgCbtwqZ$C51$D932341$Ev1.3$FXvfaPcSrgJw25VKrcsphdbyEVjmHrH1V%Z3603$X13$W000AF001AF002AH003AG004AG005AG006AF007AH008AG009AF010AF011AE012AC013AH014AC015AF016AA017AB018AE019AB020AC021AC022AF023AF024AA025AH026AF027AD028AA029AB030AG031AD032AB033AG034AF035AH036AF037AE038AC039AE040AG041AA042AE043AH044AB045AE046AE047AB048AH049AF050AG051AA052AE053AE054AA055AD056AA057AB058AC059AG060AH061AG062AE063AG064AD065AF066AC067AG068AB069AH070AA071AF072AE073AF074AE075AB076AG077AC078AA079AB080AE081AD082AD083AA084AF085AD086AG087AA088AD089AB090AG091AG092AB093AA094AC095AE096AF097AG098AG099AE100AD101AE102AB103AB104AF105AE106AH107AC108AH109AE110AE111AA112AE113AG114AC115AC116AB117AB118AD119AD120AA121AC122AA123AF124AC125AG126AD127AD128AE129AG130AC131AE132AE133AB134AB135AE136AE137AE138AG139AH140AA141AG142AH143AH144AE145AB146AG147AF148AC149AH150AC151AA152AF153AA154AG155AH156AE157AG158AD159AH160AH161AB162AA163AC164AH165AB166AB167AA168AC169AF170AB171AB172AE173AA174AA175AA176AE177AE178AD179AE180AC181AA182AC183AG184AF185AF186AH187AB188AF189AE190AC191AB192AE193AB194AB195AC196AA197AE198AD199AH200AH201AA202AD203AE204AG205AB206AB207AF208AF209AB210AE211AG212AA213AB214AD215AA216AG217AB218AG219AA220AA221AE222AF223AG224AF225AG226AE227AC228AH229AA230AH231AF232AH233AB234AF235AF236AG237AG238AE239AD240AD241AE242AA243AH244AH245AB246AC247AF248AD249AF250AG251AH252AH253AD254AC255AB256AG257AG258AG259AC260AC261AF262AA263AG264AE265AG266AH267AD268AG269AA270AH271AD272AH273AF274AG275AG276AE277AD278AB279AH280AA281AG282AE283AG284AC285AH286AG287AD288AG289AC290AB291AA292AH293AC294AC295AG296AD297AA298AG299AD300AF301AB302AE303AG304AC305AF306AC307AA308AE309AF310AC311AG312AD313AG314AA315AA316AG317AF318AB319AH320AE321AC322AE323AD324AD325AA326AA327AE328AC329AG330AE331AD332AH333AC334AC335AE336AH337AE338AE339AE340AA341AD342AF343AG344AH345AD346AE347AH348AB349AF350AH351AE352AG353AD354AC355AG356AB357AH358AA359AE360AC361AH362AD363AA364AD365AD366AG367AG368AF369AA370AA371AC372AG373AD374AD375AH376AD377AG378AC379AE380AD381AA382AF383AG384AF385AF386AE387AE388AA389AF390AE391AA392AD393AA394AC395AE396AH397AH398AA399AC400AC401AH402AC403AD404AB405AH406AG407AE408AA409AH410AE411AG412AB413AG414AC415AH416AB417AG418AD419AB420AH421AA422AB423AE424AC425AH426AE427AB428AE429AA430AH431AH432AG433AG434AH435AD436AF437AC438AB439AA440AH441AB442AH443AA444AC445AC446AE447AG448AC449AH450AH451AB452AF453AF454AC455AD456AD457AE458AC459AH460AC461AB462AH463AD464AA465AH466AC467AF468AC469AA470AF471AC472AG473AF474AA475AC476AB477AC478AG479AC480AE481AB482AG483AA484AF485AA486AA487AH488AB489AH490AG491AF492AC493AH494AF495AD496AA497AD498AE499AD500AE501AF502AB503AH504AE505AC506AF507AA508AG509AC510AH511AF512AA513AH514AC515AG516AF517AF518AD519AD520AC521AA522AE523AC524AA525AH526AF527AA528AA529AB530AH531AH532AG533AD534AB535AF536AB537AD538AG539AB540AG541AF542AD543AD544AC545AB546AD547AH548AB549AB550AF551AC552AH553AA554AF555AE556AD557AG558AF559AE560AF561AB562AE563AA564AG565AC566AA567AC568AG569AF570AF571AG572AA573AA574AH575AD576AD577AD578AC579AC580AB581AF582AG583AA584AG585AC586AB587AD588AH589AF590AF591AH592AC593AH594AE595AB596AG597AH598AC599AG600AD601AC602AD603AG604AD605AH606AE607AA608AA609AG610AF611AF612AG613AB614AA615AB616AG617AD618AG619AC620AG621AF622AG623AC624AH625AA626AD627AF628AF629AC630AB631AE632AF633AB634AG635AH636AE637AD638AD639AH640AH641AB642AA643AE644AG645AD646AE647AB648AA649AH650AF651AD652AF653AA654AB655AB656AG657AF658AG659AA660AG661AG662AD663AA664AA665AE666AE667AC668AE669AG670AF671AE672AD673AG674AF675AA676AG677AD678AH679AD680AA681AE682AD683AE684AE685AA686AH687AA688AD689AF690AB691AF692AD693AG694AG695AE696AB697AE698AG699AF700AH701AF702AE703AH704AE705AD706AD707AE708AF709AF710AC711AE712AF713AH714AA715AF716AG717AH718AA719AC720AA721AB722AD723AD724AF725AH726AD727AE728AH729AD730AA731AB732AD733AE734AB735AF736AC737AA738AF739AE740AF741AB742AG743AB744AH745AH746AF747AD748AD749AG750AD751AB752AE753AF754AE755AD756AF757AE758AG759AD760AF761AA762AC763AE764AD765AH766AG767AG768AA769AE770AE771AH772AB773AC774AG775AD776AG777AB778AH779AA780AD781AF782AA783AD784AF785AC786AH787AE788AC789AA790AC791AG792AB793AG794AF795AD796AA797AC798AG799AE800AE801AA802AA803AH804AB805AG806AD807AE808AD809AE810AE811AD812AH813AC814AF815AE816AD817AA818AF819AF820AD821AD822AD823AG824AF825AE826AC827AD828AD829AF830AG831AG832AB833AD834AB835AE836AB837AE838AG839AD840AG841AF842AD843AG844AA845AH846AE847AA848AB849AE850AH851AF852AE853AA854AF855AD856AC857AA858AH859AB860AF861AC862AB863AH864AC865AG866AF867AE868AD869AD870AH871AG872AH873AE874AB875AC876AF877AE878AB879AF880AA881AH882AF883AD884AD885AH886AH887AC888AF889AA890AG891AC892AD893AC894AD895AC896AC897AE898AE899AC900AC901AC902AF903AG904AH905AG906AA907AB908AG909AA910AB911AF912AC913AH914AF915AB916AG917AB918AB919AA920AD921AD922AF923AC924AB925AD926AD927AA928AH929AG930AA931AF932AA933AB934AG935AG936AD937AF938AG939AA940AH941AE942AC943AE944AB945AG946AD947AD948AB949AE950AG951AH952AG953AA954AG955AC956AH957AB958AC959AA960AG961AC962AC963AD964AC965AA966AG967AD968AF969AE970AB971AF',
                'blocklisted': False,
                'epoch_time': curr_time.timestamp(),
                'readable_time': curr_time.strftime('%D - %H:%M:%S')
            },
            {
                'data': '*A19$BY$C19$D23789$Ev1.3$FoV5tmZ1oWu%B304:7730:7582:8060:506:7178:2076:8471:1809:3746:5738:3741:2095:1962:4544:1084:8282:1648:9409:8256:6514:1284:9998$A8282:506:5738:8256:7582:9409:3741:304:1809:7730:4544:1962:6514:3746:8060:2076:1284:1648:7178:2095:1084:8471:9998',
                'blocklisted': False,
                'epoch_time': curr_time.timestamp(),
                'readable_time': curr_time.strftime('%D - %H:%M:%S')
            }
        ])
        self.test_decompressor.run()
        result_obj = self.test_server.db.find('unconsolidated_obj_tim')
        result_sbj = self.test_server.db.find('subj_aim')
        assert len(result_obj) == 1
        assert len(result_sbj) == 1
        result_obj, result_sbj = result_obj[0], result_sbj[0]
        result_obj.pop('_id')
        result_sbj.pop('_id')
        assert result_obj == expected_obj
        assert result_sbj == expected_sbj

    def test_get_qr_type(self):
        # Test when QRType.OBJECTIVE returns when first character is '+'
        assert decompressor.QRType.OBJECTIVE == self.test_decompressor.get_qr_type('+')
        # Test when QRType.SUBJECTIVE returns when first character is '*'
        assert decompressor.QRType.SUBJECTIVE == self.test_decompressor.get_qr_type('*')

        # Test if correct error runs when neither '+' or '*' is the first character
        with pytest.raises(ValueError) as char_error:
            self.test_decompressor.get_qr_type('a')
        assert 'QR type unknown' in str(char_error)
