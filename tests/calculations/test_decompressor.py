import datetime

import pytest
from unittest.mock import patch

import server
from calculations import decompressor


@pytest.mark.clouddb
class TestDecompressor:
    def setup_method(self, method):
        with patch('server.Server.ask_calc_all_data', return_value=False):
            self.test_server = server.Server()
        self.test_decompressor = decompressor.Decompressor(self.test_server)

    def test___init__(self):
        assert self.test_decompressor.server == self.test_server
        assert self.test_decompressor.watched_collections == ['raw_qr']


    def test_convert_data_type(self):
        # List of compressed names and decompressed names of enums
        action_type_dict = {
            'AA': 'score_ball_high_hub',
            'AB': 'score_ball_high_launchpad',
            'AC': 'score_ball_high_other',
            'AD': 'score_ball_low',
            'AE': 'intake',
            'AF': 'catch_exit_ball',
            'AG': 'score_opponent_ball',       
            'AH': 'start_incap',
            'AI': 'end_incap',
            'AJ': 'start_climb',
            'AK': 'end_climb'
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
        for compressed, decompressed in action_type_dict.items():
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
        assert '_team_separator' == self.test_decompressor.get_decompressed_name('#', 'subjective_aim')
        assert 'scout_id' == self.test_decompressor.get_decompressed_name('Y', 'objective_tim')
        assert 'start_position' == self.test_decompressor.get_decompressed_name('X', 'objective_tim')
        assert 'field_awareness_score' == self.test_decompressor.get_decompressed_name('C', 'subjective_aim')
        assert 'score_ball_high_hub' == self.test_decompressor.get_decompressed_name('AA', 'action_type')
        assert 'end_climb' == self.test_decompressor.get_decompressed_name('AK', 'action_type')
        assert 'climb_level' == self.test_decompressor.get_decompressed_name('V', 'objective_tim')
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
        assert {'schema_version': 3, 'scout_name': 'Name'} == self.test_decompressor.decompress_data(
            ['A3', 'FName'], 'generic_data'
        )
        # Test objective tim
        assert {'team_number': 1678} == self.test_decompressor.decompress_data(['Z1678'], 'objective_tim')
        # Test timeline decompression
        assert {
                   'timeline': [{'action_type': 'score_ball_high_hub', 'time': 51}]
               } == self.test_decompressor.decompress_data(['W051AA'], 'objective_tim')
        # Test using list with internal separators
        assert {'quickness_score': 1, 'field_awareness_score': 3} == self.test_decompressor.decompress_data(
            ['B1', 'C3'], 'subjective_aim'
        )

    def test_decompress_generic_qr(self):
        # Test if the correct error is raised when the Schema version is incorrect
        with pytest.raises(LookupError) as version_error:
            self.test_decompressor.decompress_generic_qr('A14$')
        assert 'does not match Server version' in str(version_error)
        # What decompress_generic_qr() should return
        expected_decompressed_data = {
            'schema_version': 3,
            'serial_number': 's1234',
            'match_number': 34,
            'timestamp': 1230,
            'match_collection_version_number': 'v1.3',
            'scout_name': 'Name',
        }
        assert expected_decompressed_data == self.test_decompressor.decompress_generic_qr(
            'A3$Bs1234$C34$D1230$Ev1.3$FName'
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
               ] == self.test_decompressor.decompress_timeline('060AJ061AK')
        # Should return empty list if passed an empty string
        assert [] == self.test_decompressor.decompress_timeline('')

    def test_decompress_single_qr(self):
        # Expected decompressed objective qr
        expected_objective = [
            {
                'schema_version': 3,
                'serial_number': 's1234',
                'match_number': 34,
                'timestamp': 1230,
                'match_collection_version_number': 'v1.3',
                'scout_name': 'Name',
                'team_number': 1678,
                'scout_id': 14,
                'start_position': 'THREE',
                'timeline': [
                    {'time': 60, 'action_type': 'start_climb'},
                    {'time': 61, 'action_type': 'end_climb'},
                ],
                'climb_level': 'NONE'
            }
        ]
        # Expected decompressed subjective qr
        expected_subjective = [
            {
                'schema_version': 3,
                'serial_number': 's1234',
                'match_number': 34,
                'timestamp': 1230,
                'match_collection_version_number': 'v1.3',
                'scout_name': 'Name',
                'team_number': 1678,
                'quickness_score': 1,
                'field_awareness_score': 2,
                'far_field_rating': 3,
                'scored_far': True,
                'alliance_color_is_red': True
            },
            {
                'schema_version': 3,
                'serial_number': 's1234',
                'match_number': 34,
                'timestamp': 1230,
                'match_collection_version_number': 'v1.3',
                'scout_name': 'Name',
                'team_number': 254,
                'quickness_score': 2,
                'field_awareness_score': 1,
                'far_field_rating': 1,
                'scored_far': False,
                'alliance_color_is_red': True
            },
            {
                'schema_version': 3,
                'serial_number': 's1234',
                'match_number': 34,
                'timestamp': 1230,
                'match_collection_version_number': 'v1.3',
                'scout_name': 'Name',
                'team_number': 1323,
                'quickness_score': 3,
                'field_awareness_score': 1,
                'far_field_rating': 2,
                'scored_far': True,
                'alliance_color_is_red': True
            },
        ]
        # Test objective qr decompression
        assert expected_objective == self.test_decompressor.decompress_single_qr(
            'A3$Bs1234$C34$D1230$Ev1.3$FName%Z1678$Y14$XTHREE$W060AJ061AK$VNONE', decompressor.QRType.OBJECTIVE
        )
        # Test subjective qr decompression
        assert expected_subjective == self.test_decompressor.decompress_single_qr(
            'A3$Bs1234$C34$D1230$Ev1.3$FName%A1678$B1$C2$D3$ETRUE$FTRUE#A254$B2$C1$D1$EFALSE$FTRUE#A1323$B3$C1$D2$ETRUE$FTRUE',
            decompressor.QRType.SUBJECTIVE,
        )
        # Test error raising for objective and subjective using incomplete qrs
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                'A3$Bs1234$C34$D1230$Ev1.3$FName%Z1678$Y14', decompressor.QRType.OBJECTIVE
            )
        assert 'QR missing data fields' in str(excinfo)
        with pytest.raises(IndexError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                'A3$Bs1234$C34$D1230$Ev1.3$FName%A1678$B1$C2$D3$EFALSE', decompressor.QRType.SUBJECTIVE
            )
        assert 'Incorrect number of teams in Subjective QR' in str(excinfo)
        with pytest.raises(ValueError) as excinfo:
            self.test_decompressor.decompress_single_qr(
                'A3$Bs1234$C34$D1230$Ev1.3$FName%A1678$B1$C2#A254#A1323', decompressor.QRType.SUBJECTIVE
            )
        assert 'QR missing data fields' in str(excinfo)

    def test_decompress_qrs(self):
        # Expected output from a list containing one obj qr and one subj qr
        expected_output = {
            'unconsolidated_obj_tim': [
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1678,
                    'scout_id': 14,
                    'start_position': 'FOUR',
                    'timeline': [
                        {'time': 60, 'action_type': 'start_climb'},
                        {'time': 61, 'action_type': 'end_climb'},
                    ],
                    'climb_level': 'HIGH'
                }
            ],
            'subj_tim': [
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1678,
                    'quickness_score': 1,
                    'field_awareness_score': 2,
                    'far_field_rating': 3,
                    'scored_far': False,
                    'alliance_color_is_red': False
                },
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 254,
                    'quickness_score': 2,
                    'field_awareness_score': 2,
                    'far_field_rating': 1,
                    'scored_far': False,
                    'alliance_color_is_red': False
                },
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1323,
                    'quickness_score': 3,
                    'field_awareness_score': 3,
                    'far_field_rating': 2,
                    'scored_far': True,
                    'alliance_color_is_red': False
                },
            ],
        }
        assert expected_output == self.test_decompressor.decompress_qrs(
            [
                {'data': '+A3$Bs1234$C34$D1230$Ev1.3$FName%Z1678$Y14$XFOUR$W060AJ061AK$VHIGH'},
                {'data': '*A3$Bs1234$C34$D1230$Ev1.3$FName%A1678$B1$C2$D3$EFALSE$FFALSE#A254$B2$C2$D1$EFALSE$FFALSE#A1323$B3$C3$D2$ETRUE$FFALSE'},
            ]
        )

    def test_run(self):
        expected_obj = {
            'schema_version': 3,
            'serial_number': 'gCbtwqZ',
            'match_number': 51,
            'timestamp': 9321,
            'match_collection_version_number': 'v1.3',
            'scout_name': 'XvfaPcSrgJw25VKrcsphdbyEVjmHrH1V',
            'team_number': 3603,
            'scout_id': 13,
            'start_position': 'ONE',
            'timeline': [
                {
                    'time': 0,
                    'action_type': 'score_ball_high_launchpad'
                },
                {
                    'time': 1,
                    'action_type': 'score_ball_low'
                },
                {
                    'time': 2,
                    'action_type': 'intake'
                },
                {
                    'time': 3,
                    'action_type': 'catch_exit_ball'
                },
                {
                    'time': 4,
                    'action_type': 'score_opponent_ball'
                },
                {
                    'time': 5,
                    'action_type': 'score_ball_high_other'
                },
                {
                    'time': 6,
                    'action_type': 'score_ball_low'
                },
                {
                    'time': 7,
                    'action_type': 'start_incap'
                },
                {
                    'time': 8,
                    'action_type': 'end_incap'
                },
                {
                    'time': 9,
                    'action_type': 'start_climb'
                },
                {
                    'time': 10,
                    'action_type': 'end_climb'
                }
            ],
            'climb_level': 'TRAVERSAL'
        }
        expected_sbj = [
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1678,
                    'quickness_score': 1,
                    'field_awareness_score': 2,
                    'far_field_rating': 3,
                    'scored_far': False,
                    'alliance_color_is_red': False
                },
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 254,
                    'quickness_score': 2,
                    'field_awareness_score': 2,
                    'far_field_rating': 1,
                    'scored_far': False,
                    'alliance_color_is_red': False
                },
                {
                    'schema_version': 3,
                    'serial_number': 's1234',
                    'match_number': 34,
                    'timestamp': 1230,
                    'match_collection_version_number': 'v1.3',
                    'scout_name': 'Name',
                    'team_number': 1323,
                    'quickness_score': 3,
                    'field_awareness_score': 3,
                    'far_field_rating': 2,
                    'scored_far': True,
                    'alliance_color_is_red': False
                },
            ]
        curr_time = datetime.datetime.utcnow()

        self.test_server.db.insert_documents('raw_qr', [
            {
                'data': '+A3$BgCbtwqZ$C51$D9321$Ev1.3$FXvfaPcSrgJw25VKrcsphdbyEVjmHrH1V%Z3603$Y13$XONE$W000AB001AD002AE003AF004AG005AC006AD007AH008AI009AJ010AK$VTRAVERSAL',
                'blocklisted': False,
                'epoch_time': curr_time.timestamp(),
                'readable_time': curr_time.strftime('%D - %H:%M:%S')
            },
            {
                'data': '*A3$Bs1234$C34$D1230$Ev1.3$FName%A1678$B1$C2$D3$EFALSE$FFALSE#A254$B2$C2$D1$EFALSE$FFALSE#A1323$B3$C3$D2$ETRUE$FFALSE',
                'blocklisted': False,
                'epoch_time': curr_time.timestamp(),
                'readable_time': curr_time.strftime('%D - %H:%M:%S')
            }
        ])
        self.test_decompressor.run()
        result_obj = self.test_server.db.find('unconsolidated_obj_tim')
        result_sbj = self.test_server.db.find('subj_tim')
        assert len(result_obj) == 1
        assert len(result_sbj) == 3
        result_obj = result_obj[0]
        result_obj.pop('_id')
        assert result_obj == expected_obj
        for result in result_sbj:
            result.pop('_id')
            assert result in expected_sbj

    def test_get_qr_type(self):
        # Test when QRType.OBJECTIVE returns when first character is '+'
        assert decompressor.QRType.OBJECTIVE == self.test_decompressor.get_qr_type('+')
        # Test when QRType.SUBJECTIVE returns when first character is '*'
        assert decompressor.QRType.SUBJECTIVE == self.test_decompressor.get_qr_type('*')

        # Test if correct error runs when neither '+' or '*' is the first character
        with pytest.raises(ValueError) as char_error:
            self.test_decompressor.get_qr_type('a')
        assert 'QR type unknown' in str(char_error)
