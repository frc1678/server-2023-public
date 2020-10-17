import pytest

from calculations import decompressor


def test_get_data_fields():
    # Set of what the data fields should be
    expected_data_fields = {
        'schema_version',
        'serial_number',
        'match_number',
        'timestamp',
        'match_collection_version_number',
        'scout_name',
    }
    # Test that it returns the correct data type
    assert isinstance(decompressor._get_data_fields('generic_data'), set)
    # Test that the returned fields match what is expected
    assert expected_data_fields == decompressor._get_data_fields('generic_data')


def test_convert_data_type():
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
    assert 5 == decompressor.convert_data_type('5', 'int')
    assert 6 == decompressor.convert_data_type(6.43, 'int')
    assert 5.0 == decompressor.convert_data_type('5', 'float')
    assert 6.32 == decompressor.convert_data_type('6.32', 'float')
    assert 3.0 == decompressor.convert_data_type(3, 'float')
    assert decompressor.convert_data_type('1', 'bool')
    assert decompressor.convert_data_type('T', 'bool')
    assert decompressor.convert_data_type('TRUE', 'bool')
    assert not decompressor.convert_data_type('0', 'bool')
    assert not decompressor.convert_data_type('F', 'bool')
    assert not decompressor.convert_data_type('FALSE', 'bool')
    assert '' == decompressor.convert_data_type('', 'str')
    # Test all enums
    for compressed, decompressed in enum_dict.items():
        assert decompressed == decompressor.convert_data_type(
            compressed, 'Enum', name='action_type'
        )
    # Test error raising
    with pytest.raises(ValueError) as type_error:
        decompressor.convert_data_type('', 'tuple')
    assert 'Type tuple not recognized' in str(type_error.value)


def test_get_decompressed_name():
    # Test for the that '$' returns '_separator' in all 3 sections that have it
    sections = ['generic_data', 'objective_tim', 'subjective_aim']
    for section in sections:
        assert '_separator' == decompressor.get_decompressed_name('$', section)
    # Test for a name with a string and a name with a list from each section
    assert '_section_separator' == decompressor.get_decompressed_name('%', 'generic_data')
    assert 'serial_number' == decompressor.get_decompressed_name('B', 'generic_data')
    assert 'timeline' == decompressor.get_decompressed_name('W', 'objective_tim')
    assert '_start_character' == decompressor.get_decompressed_name('+', 'objective_tim')
    assert 'time' == decompressor.get_decompressed_name(3, 'timeline')
    assert '_start_character' == decompressor.get_decompressed_name('*', 'subjective_aim')
    assert '_separator_internal' == decompressor.get_decompressed_name(':', 'subjective_aim')
    assert 'agility_rankings' == decompressor.get_decompressed_name('B', 'subjective_aim')
    assert 'score_ball_high' == decompressor.get_decompressed_name('AA', 'action_type')
    assert 'end_climb' == decompressor.get_decompressed_name('AH', 'action_type')
    with pytest.raises(ValueError) as excinfo:
        decompressor.get_decompressed_name('#', 'generic_data')
    assert 'Retrieving Variable Name # from generic_data failed.' in str(excinfo)


def test_get_decompressed_type():
    # Test when there are two values in a list
    assert 'int' == decompressor.get_decompressed_type('schema_version', 'generic_data')
    assert 'str' == decompressor.get_decompressed_type('serial_number', 'generic_data')
    # Test when list has more than two values
    assert ['list', 'dict'] == decompressor.get_decompressed_type('timeline', 'objective_tim')


def test_decompress_data():
    # Test generic data
    assert {'schema_version': 18, 'scout_name': 'Name'} == decompressor.decompress_data(
        ['A18', 'FName'], 'generic_data'
    )
    # Test objective tim
    assert {'team_number': 1678} == decompressor.decompress_data(['Z1678'], 'objective_tim')
    # Test timeline decompression
    assert {
        'timeline': [{'action_type': 'score_ball_low', 'time': 51}]
    } == decompressor.decompress_data(['W051AB'], 'objective_tim')
    # Test using list with internal separators
    assert {'rendezvous_agility_rankings': [1678, 1323, 254]} == decompressor.decompress_data(
        ['A1678:1323:254'], 'subjective_aim'
    )


def test_decompress_generic_qr():
    # Test if the correct error is raised when the Schema version is incorrect
    with pytest.raises(LookupError) as version_error:
        decompressor.decompress_generic_qr('A14$')
    assert 'does not match Server version' in str(version_error)
    # What decompress_generic_qr() should return
    expected_decompressed_data = {
        'schema_version': 18,
        'serial_number': 's1234',
        'match_number': 34,
        'timestamp': 1230,
        'match_collection_version_number': 'v1.3',
        'scout_name': 'Name',
    }
    assert expected_decompressed_data == decompressor.decompress_generic_qr(
        'A18$Bs1234$C34$D1230$Ev1.3$FName'
    )


def test_get_timeline_info():
    # What get_timeline_info() should return
    expected_timeline_info = [
        {'name': 'time', 'length': 3, 'type': 'int', 'position': 0},
        {'name': 'action_type', 'length': 2, 'type': 'Enum', 'position': 1},
    ]
    assert expected_timeline_info == decompressor.get_timeline_info()


def test_decompress_timeline():
    # Function should raise an error if the data isn't the right length
    with pytest.raises(ValueError) as excinfo:
        decompressor.decompress_timeline(['abcdefg'])
    assert 'Invalid timeline -- Timeline length invalid: [\'abcdefg\']' in str(excinfo)
    # Test timeline decompression
    assert [
        {'time': 60, 'action_type': 'start_climb'},
        {'time': 61, 'action_type': 'end_climb'},
    ] == decompressor.decompress_timeline('060AG061AH')
    # Should return empty list if passed an empty string
    assert [] == decompressor.decompress_timeline('')


def test_decompress_single_qr():
    # Expected decompressed objective qr
    expected_objective = {
        'schema_version': 18,
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
        'schema_version': 18,
        'serial_number': 's1234',
        'match_number': 34,
        'timestamp': 1230,
        'match_collection_version_number': 'v1.3',
        'scout_name': 'Name',
        'rendezvous_agility_rankings': [1678, 1323, 254],
        'agility_rankings': [1323, 1678, 254],
    }
    # Test objective qr decompression
    assert expected_objective == decompressor.decompress_single_qr(
        'A18$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14$W060AG061AH', decompressor.QRType.OBJECTIVE
    )
    # Test subjective qr decompression
    assert expected_subjective == decompressor.decompress_single_qr(
        'A18$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254$B1323:1678:254',
        decompressor.QRType.SUBJECTIVE,
    )
    # Test error raising for objective and subjective using incomplete qrs
    with pytest.raises(ValueError) as excinfo:
        decompressor.decompress_single_qr(
            'A18$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14', decompressor.QRType.OBJECTIVE
        )
    assert 'QR missing data fields' in str(excinfo)
    with pytest.raises(ValueError) as excinfo:
        decompressor.decompress_single_qr(
            'A18$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254', decompressor.QRType.SUBJECTIVE
        )
    assert 'QR missing data fields' in str(excinfo)


def test_decompress_qrs():
    # Expected output from a list containing one obj qr and one subj qr
    expected_output = {
        'unconsolidated_obj_tim': [
            {
                'schema_version': 18,
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
                'schema_version': 18,
                'serial_number': 's1234',
                'match_number': 34,
                'timestamp': 1230,
                'match_collection_version_number': 'v1.3',
                'scout_name': 'Name',
                'rendezvous_agility_rankings': [1678, 1323, 254],
                'agility_rankings': [1323, 1678, 254],
            }
        ],
    }
    assert expected_output == decompressor.decompress_qrs(
        [
            '+A18$Bs1234$C34$D1230$Ev1.3$FName%Z1678$X14$W060AG061AH',
            '*A18$Bs1234$C34$D1230$Ev1.3$FName%A1678:1323:254$B1323:1678:254',
        ]
    )


def test_get_qr_type():
    # Test when QRType.OBJECTIVE returns when first character is '+'
    assert decompressor.QRType.OBJECTIVE == decompressor.get_qr_type('+')
    # Test when QRType.SUBJECTIVE returns when first character is '*'
    assert decompressor.QRType.SUBJECTIVE == decompressor.get_qr_type('*')

    # Test if correct error runs when neither '+' or '*' is the first character
    with pytest.raises(ValueError) as char_error:
        decompressor.get_qr_type('a')
    assert 'QR type unknown' in str(char_error)
