from unittest import mock

import pytest

import server
from data_transfer import database, cloud_db_updater


@pytest.mark.clouddb
class TestServer:
    @mock.patch('server.Server.load_calculations')
    def test_init(self, mock_load):
        with mock.patch('server.Server.ask_calc_all_data', return_value=True):
            s = server.Server(write_cloud=True)
        # Load calculations is mocked out, so calculations list should  be empty
        assert s.calculations == mock_load.return_value
        assert isinstance(s.db, database.Database)
        assert isinstance(s.cloud_db_updater, cloud_db_updater.CloudDBUpdater)
        assert s.calc_all_data == True
        mock_load.assert_called_once()

    @mock.patch('server.importlib.import_module')
    @mock.patch('server.yaml.load', return_value=[{'import_path': 'a.b', 'class_name': 'test'}])
    def test_load_calculations(self, mock_calc_dict, mock_import):
        with mock.patch('server.Server.ask_calc_all_data', return_value=False):
            s = server.Server()
        calcs = s.load_calculations()
        assert calcs == [mock_import.return_value.test()]

    @mock.patch('server.Server.ask_calc_all_data', return_value=False)
    @mock.patch('server.utils.log_error')
    @mock.patch('server.yaml.load', return_value=[{'import_path': 'a.b', 'class_name': 'test'}])
    def test_load_calculations_import_error(self, mock_calc_dict, mock_log, mock_calc_all_data):
        def f(path):
            raise SyntaxError(f'Error in {path}')

        with mock.patch('server.importlib.import_module', side_effect=f):
            s = server.Server()
            assert s.calculations == []

        mock_log.assert_called_with('SyntaxError importing a.b: Error in a.b')

    @mock.patch('server.Server.ask_calc_all_data', return_value=False)
    @mock.patch('server.utils.log_error')
    @mock.patch('server.yaml.load', return_value=[{'import_path': 'a.b', 'class_name': 'test'}])
    def test_load_calculations_calc_init_error(self, mock_calc_dict, mock_log, mock_calc_all_data):
        def f(server):
            raise ValueError('Error in calculation')

        mocked_import = mock.MagicMock()
        mocked_import.test = f

        with mock.patch('server.importlib.import_module', return_value=mocked_import):
            s = server.Server()
            assert s.calculations == []

        mock_log.assert_called_with('ValueError instantiating a.b.test: Error in calculation')

    @mock.patch('server.Server.ask_calc_all_data', return_value=False)
    def test_run_calculations(self, mock_calc_all_data):
        calcs = [mock.MagicMock(), mock.MagicMock()]
        with mock.patch('server.Server.load_calculations', return_value=calcs) as _:
            s = server.Server()
        s.run_calculations()
        for c in calcs:
            c.run.assert_called_once()
