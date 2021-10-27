from calculations import compression


def test_compress_timeline():
    timeline_data = [
        {'time': 51, 'action_type': 'start_incap'},
        {'time': 32, 'action_type': 'end_incap'},
    ]
    assert compression.compress_timeline(timeline_data) == '051AC032AD'
    timeline_data[1]['action_type'] = 'score_ball_high'
    assert compression.compress_timeline(timeline_data) == '051AC032AA'


def test_compress_list():
    test_list = [1, 2, 3]
    assert compression.compress_list('subjective_aim', test_list) == '1:2:3'


def test_compress_section_generic_data():
    # Make sure it adds schema version
    assert compression.compress_section({}, 'generic_data') == 'A19'
    # Check generic data compression
    schema_data = {'schema_version': 19}
    compressed_schema = 'A19'
    assert compression.compress_section(schema_data, 'generic_data') == compressed_schema
    # Check multiple points
    schema_data['serial_number'] = 'test'
    # Qrs are only uppercase
    compressed_schema += '$BTEST'
    assert compression.compress_section(schema_data, 'generic_data') == compressed_schema


def test_compress_section_obj():
    # Without timeline
    schema_data = {'team_number': 1678, 'scout_id': 18}
    compressed_schema = 'Z1678$X18'
    assert compression.compress_section(schema_data, 'objective_tim') == compressed_schema
    # With timeline
    schema_data['timeline'] = [{'time': 51, 'action_type': 'start_incap'}]
    compressed_schema += '$W051AC'
    assert compression.compress_section(schema_data, 'objective_tim') == compressed_schema


def test_compress_section_subj():
    data = {'quickness_rankings': [1, 2, 3], 'field_awareness_rankings': [2, 3, 1]}
    assert compression.compress_section(data, 'subjective_aim') == 'A1:2:3$B2:3:1'


def test_compress_obj_tim():
    data = {
        'schema_version': 19,
        'serial_number': 'HASAMPLENUM',
        'match_number': 1,
        'timestamp': 1582994470,
        'match_collection_version_number': '1.0.2',
        'team_number': 9999,
        'scout_name': 'KEVIN R',
        'scout_id': 2,
        'timeline': [
            {'time': 45, 'action_type': 'start_incap'},
            {'time': 7, 'action_type': 'end_incap'},
        ],
    }
    compressed_data = '+A19$BHASAMPLENUM$C1$D1582994470$E1.0.2$FKEVIN R%Z9999$X2$W045AC007AD'
    assert compression.compress_obj_tim(data) == compressed_data


def test_compress_subj_aim():
    data = {
        'schema_version': 19,
        'serial_number': 'HASAMPLENUM',
        'match_number': 1,
        'timestamp': 1582994470,
        'match_collection_version_number': '1.0.2',
        'team_number': 9999,
        'scout_name': 'KEVIN R',
        'quickness_rankings': [1, 2, 3],
        'field_awareness_rankings': [2, 3, 1],
    }
    compressed_data = '*A19$BHASAMPLENUM$C1$D1582994470$E1.0.2$FKEVIN R%A1:2:3$B2:3:1'
    assert compression.compress_subj_aim(data) == compressed_data
