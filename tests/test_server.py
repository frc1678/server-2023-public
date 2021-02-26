from unittest import mock

import pytest

import server
from data_transfer import database, cloud_db_updater


@pytest.mark.clouddb
class TestServer:
    @mock.patch('server.Server.load_calculations')
    def test_init(self, mock_load):
        s = server.Server()
        # Load calculations is mocked out, so calculations list should  be empty
        assert s.calculations == mock_load.return_value
        assert isinstance(s.db, database.Database)
        assert isinstance(s.cloud_db_updater, cloud_db_updater.CloudDBUpdater)
        mock_load.assert_called_once()

    @mock.patch('server.importlib.import_module')
    @mock.patch('server.yaml.load', return_value=[{'import_path': 'a.b', 'class_name': 'test'}])
    def test_load_calculations(self, mock_calc_dict, mock_import):
        s = server.Server()
        calcs = s.load_calculations()
        assert calcs == [mock_import.return_value.test()]

    def test_run_calculations(self):
        calcs = [mock.MagicMock(), mock.MagicMock()]
        with mock.patch('server.Server.load_calculations', return_value=calcs) as _:
            s = server.Server()
        s.run_calculations()
        for c in calcs:
            c.run.assert_called_once()
