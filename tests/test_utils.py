import re
import os


def test_constants():
    import utils

    # Check main directory
    assert __file__.startswith(str(utils.MAIN_DIRECTORY))
    assert re.search(r'server(-2020)?[/\\]?$', str(utils.MAIN_DIRECTORY))
    assert os.path.exists(utils.MAIN_DIRECTORY)


def test_create_file_path():
    import utils

    # Test that it creates path by default
    path = utils.create_file_path('test_file_path')
    assert path == os.path.join(utils.MAIN_DIRECTORY, 'test_file_path')
    assert os.path.exists(path)

    # Test that it does not create if create_directories=False
    os.rmdir(path)
    path_not_created = utils.create_file_path('test_file_path', False)
    assert path == path_not_created
    assert not os.path.exists(path_not_created)
