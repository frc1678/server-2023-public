# Copyright (c) 2019-2020 FRC Team 1678: Citrus Circuits

import pytest

import server
from calculations import compression
from calculations import decompressor
import generate_test_qrs
import utils

SCHEMA = utils.read_schema('schema/match_collection_qr_schema.yml')
DECOMPRESSOR = decompressor.Decompressor(server.Server())


def test_generate_type_data():
    # Makes sure that when you pass in a specific type, it returns the correct type
    assert isinstance(generate_test_qrs.generate_type_data('str'), str)
    assert isinstance(generate_test_qrs.generate_type_data('int'), int)
    assert isinstance(generate_test_qrs.generate_type_data('bool'), bool)
    with pytest.raises(ValueError):
        generate_test_qrs.generate_type_data('NA Type')


def test_generate_timeline():
    # Generates a timeline using the function to do tests with
    timeline = generate_test_qrs.generate_timeline()

    # Makes sure every action in the timeline is valid
    for action in timeline:
        assert 0 <= action['time'] <= 150
        assert action['action_type'] in list(SCHEMA['action_type'].keys())


def test_generate_generic_data():
    generic_data = generate_test_qrs.generate_generic_data(14, 'Bobby')
    # Check that all the data fields exist in the generic data
    for field in list(SCHEMA['generic_data'].keys()):
        if not field.startswith('_'):
            assert field in list(generic_data.keys())

    # Check that the parameters exist in the final returned data
    assert generic_data['match_number'] == 14
    assert generic_data['scout_name'] == 'Bobby'


def test_generate_obj_tim():
    obj_tim_qr = generate_test_qrs.generate_obj_tim()
    # Decompress and Compress the data to make sure the qr is valid
    decompressed_qr = DECOMPRESSOR.decompress_single_qr(
        obj_tim_qr[1:], decompressor.QRType.OBJECTIVE
    )
    assert compression.compress_obj_tim(decompressed_qr) == obj_tim_qr


def test_generate_subj_aim():
    subj_aim_qr = generate_test_qrs.generate_subj_aim()
    # Decompress and Compress the data to make sure the qr is valid
    decompressed_qr = DECOMPRESSOR.decompress_single_qr(
        subj_aim_qr[1:], decompressor.QRType.SUBJECTIVE
    )
    assert compression.compress_subj_aim(decompressed_qr) == subj_aim_qr
