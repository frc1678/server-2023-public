from calculations import pickability
from server import Server

from unittest import mock

import pytest


FAKE_SCHEMA = {
    'calculations': {
        'first_pickability': {
            'requires': [
                'test.datapoint1',
                'test.datapoint2',
                'test2.datapoint1',
            ],
            'weights': [1, 1, 1],
        },
        'second_pickability': {
            'requires': [
                'test.datapoint1',
                'test.datapoint2',
                'test2.datapoint1',
            ],
            'weights': [1, 1, 2],
        },
    }
}


@pytest.mark.clouddb
class TestPickability:
    @staticmethod
    def test__init__():
        m_server = Server()
        with mock.patch('utils.read_schema', return_value=FAKE_SCHEMA):
            test_calc = pickability.PickabilityCalc(m_server)
        assert test_calc.server == m_server
        assert 'test' in test_calc.watched_collections and 'test2' in test_calc.watched_collections
        assert {
            'first_pickability': [
                ('test', 'datapoint1'),
                ('test', 'datapoint2'),
                ('test2', 'datapoint1'),
            ],
            'second_pickability': [
                ('test', 'datapoint1'),
                ('test', 'datapoint2'),
                ('test2', 'datapoint1'),
            ],
        } == test_calc.calcs

    @staticmethod
    @mock.patch('utils.read_schema', return_value=FAKE_SCHEMA)
    def test_calculate_pickabilty(mock):
        test_calc = pickability.PickabilityCalc(Server())
        calc_data = {
            'test': {
                'team_number': 0,
                'datapoint1': 2,
                'datapoint2': 1,
                'useless': None,
            },
            'test2': {'team_number': 0, 'datapoint1': 3, 'useless': None},
        }
        assert test_calc.calculate_pickability(0, 'first_pickability', calc_data) == 2
        assert test_calc.calculate_pickability(0, 'second_pickability', calc_data) == 2.25
        assert test_calc.calculate_pickability(0, 'first_pickability', {}) is None
        # Check that if the datapoint is missing that it correctly returns None
        calc_data = {
            'test': {
                'team_number': 0,
                'datapoint2': 1,
                'useless': None,
            },
            'test2': {'team_number': 0, 'datapoint1': 3, 'useless': None},
        }
        assert test_calc.calculate_pickability(0, 'first_pickability', calc_data) is None

    @staticmethod
    @mock.patch('utils.read_schema', return_value=FAKE_SCHEMA)
    def test_run(mock):
        server_obj = Server()
        test_calc = pickability.PickabilityCalc(server_obj)
        # This is not enough to do a pickability calc, it needs the test2 datapoint
        server_obj.db.insert_documents('test', {'team_number': 0, 'datapoint1': 1, 'datapoint2': 5})
        test_calc.run()
        assert server_obj.db.find('pickability') == []
        # Insert all the required data
        server_obj.db.insert_documents(
            'test2', {'team_number': 0, 'datapoint1': 1, 'datapoint2': 5}
        )
        test_calc.run()
        result = server_obj.db.find('pickability')
        # Check that a result was added
        assert result
        server_obj.db.delete_data('test2', **{})
        server_obj.db.insert_documents(
            'test2', {'team_number': 0, 'datapoint1': 2000000, 'datapoint2': 20}
        )
        test_calc.run()
        new_result = server_obj.db.find('pickability')
        assert result != new_result
