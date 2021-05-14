import server

import datetime
from unittest import mock

import pytest

FAKE_SCHEMA = {
    'objective_tim': {'_start_character': '+'},
    'subjective_aim': {'_start_character': '*'},
}


@pytest.mark.clouddb
class TestQRInput:
    def setup(self):
        self.server = server.Server()

    def test_run(self, capsys):
        with mock.patch('utils.read_schema', return_value=FAKE_SCHEMA), mock.patch(
            'builtins.open', mock.mock_open(read_data='1,1,1')
        ), mock.patch('json.load', return_value={}):
            from calculations import qr_input

            self.test_calc = qr_input.QRInput(self.server)
        with mock.patch('data_transfer.adb_communicator.pull_device_data', return_value=[]):
            with mock.patch('builtins.input', return_value='*test'):
                self.test_calc.run()
                assert (query := self.server.db.find("raw_qr")) != []
                assert 'data' in query[0].keys() and query[0]['data'] == '*test'
                assert isinstance(query[0]['epoch_time'], float)
                assert isinstance(query[0]['readable_time'], str)
            with mock.patch('builtins.input', return_value='*test\ttest'):
                self.test_calc.run()
                reading = capsys.readouterr()
                assert 'WARNING: duplicate QR code not uploaded' in reading.out
                assert 'Invalid QR code not uploaded: ' in reading.err
            with mock.patch('builtins.input', return_value='*test2\t+test3\t*test4'):
                self.test_calc.run()
                assert (query := self.server.db.find('raw_qr')) != [] and len(query) == 4
