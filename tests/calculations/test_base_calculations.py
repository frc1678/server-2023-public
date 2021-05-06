import pytest

from unittest.mock import patch

from calculations.base_calculations import BaseCalculations
from server import Server


@pytest.mark.clouddb
class TestBaseCalculations:
    def setup_method(self, method):
        self.test_server = Server()
        self.base_calc = BaseCalculations(self.test_server)

    def test__init__(self):
        assert self.base_calc.server == self.test_server
        assert self.base_calc.oplog == self.test_server.db.client.local.oplog.rs
        assert self.base_calc.watched_collections == NotImplemented

    def test_update_timestamp(self):
        self.test_server.db.insert_documents('test', {'a': 1})
        self.base_calc.update_timestamp()
        op = self.base_calc.oplog.find_one({'op': 'i', 'o.a': 1})
        assert self.base_calc.timestamp >= op['ts']

    def test_entries_since_last(self):
        self.base_calc.watched_collections = ['test.testing']
        self.base_calc.update_timestamp()
        self.test_server.db.insert_documents(
            'test.testing', ({'a': 1}, {'a': 2}, {'a': 3})
        )
        self.test_server.db.delete_data('test.testing', a=1)
        self.test_server.db.update_document('test.testing', {'b': 2}, {'a': 2})
        for entry in self.base_calc.entries_since_last():
            assert entry['ts'] > self.base_calc.timestamp
            assert entry['op'] in ['d', 'i', 'u']

    def test_find_team_list(self):
        self.base_calc.update_timestamp()
        self.base_calc.watched_collections = ['test']
        self.test_server.db.insert_documents(
            'test',
            [
                {'team_number': 0},
                {'useless': 0},
                {'team_number': 1, 'useless': 0},
            ],
        )
        assert self.base_calc.find_team_list() == [0, 1]
        self.base_calc.update_timestamp()
        self.test_server.db.update_document('test', {'team_number': 1}, {'useless': 1})
        assert self.base_calc.find_team_list() == [1]

    def test_avg(self):
        # Test if there is no input
        assert 0 == BaseCalculations.avg('')
        # Test average with no weights
        assert 2 == BaseCalculations.avg([1, 2, 3])
        # Test error if there are a different amount of weights than numbers
        with pytest.raises(ValueError) as num_error:
            BaseCalculations.avg([1, 2], [3, 4, 5])
        assert 'Weighted average expects one weight for each number.' in str(num_error)
        # Test average with weights
        assert 1 == BaseCalculations.avg([1, 3], [2.0, 0.0])
