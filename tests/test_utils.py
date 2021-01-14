import re
import os

import utils


def test_constants():
    # Check main directory
    assert __file__.startswith(str(utils.MAIN_DIRECTORY))
    assert re.search(r'server(-2020)?[/\\]?$', str(utils.MAIN_DIRECTORY))
    assert os.path.exists(utils.MAIN_DIRECTORY)


def test_create_file_path():
    # Test that it creates path by default
    path = utils.create_file_path('test_file_path')
    assert path == os.path.join(utils.MAIN_DIRECTORY, 'test_file_path')
    assert os.path.exists(path)

    # Test that it does not create if create_directories=False
    os.rmdir(path)
    path_not_created = utils.create_file_path('test_file_path', False)
    assert path == path_not_created
    assert not os.path.exists(path_not_created)


def test_load_tba_event_key_file():
    with open(utils.create_file_path('data/competition.txt')) as file:
        event_key = file.read().rstrip('\n')

    # Test that the function returns what's in the correct file
    assert event_key == utils.load_tba_event_key_file('data/competition.txt')

    # Test that the function returns None when the file path is not found
    assert utils.load_tba_event_key_file('documents/downloads/desktop.txt') is None


def test_get_schema_filenames():
    schema_names = utils.get_schema_filenames()
    assert isinstance(schema_names, set)
    assert "obj_pit_collection_schema.yml" in schema_names
