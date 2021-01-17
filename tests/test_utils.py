import os
import re
import subprocess

import pytest

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


# Test logging functions

# capsys.readouterr() captures print statements
# caplog.records captures log level


def test_catch_function_errors(capsys, caplog):
    # Test function
    def test_fun():
        raise ValueError('smth')

    utils.catch_function_errors(test_fun)
    captured = capsys.readouterr()
    assert captured.out == "Function test_fun: <class 'ValueError'> - smth\n"
    for record in caplog.records:
        assert record.levelname == 'ERROR'
    assert utils.catch_function_errors(utils.avg, [1, 1]) == 1
    assert utils.catch_function_errors(utils.avg, [1, 2, 3], [1.0, 1.0]) is None


def test_log_warning(capsys, caplog):
    utils.log_warning('warning')
    captured = capsys.readouterr()
    assert captured.err == 'WARNING: warning\n'
    for record in caplog.records:
        assert record.levelname == 'WARNING'


def test_log_info(caplog):
    utils.log_info('info')
    for record in caplog.records:
        assert record.levelname == 'INFO'


def test_log_debug(caplog):
    utils.log_debug('debug')
    for record in caplog.records:
        assert record.levelname == 'DEBUG'


# End test of logging


def test_load_tba_event_key_file():
    with open(utils.create_file_path('data/competition.txt')) as file:
        event_key = file.read().rstrip('\n')

    # Test that the function returns what's in the correct file
    assert event_key == utils.load_tba_event_key_file('data/competition.txt')

    # Test that the function returns None when the file path is not found
    assert utils.load_tba_event_key_file('documents/downloads/desktop.txt') is None


def test_run_command():
    with pytest.raises(Exception) as expected_error:
        utils.run_command('foo')  # Should error
    # If 'foo' is in the message it's a useful diagnostic because we know what errored.
    assert 'foo' in str(expected_error)

    assert utils.run_command('echo foo', return_output=True) == 'foo\n'


def test_get_schema_filenames():
    schema_names = utils.get_schema_filenames()
    assert isinstance(schema_names, set)
    assert "obj_pit_collection_schema.yml" in schema_names
