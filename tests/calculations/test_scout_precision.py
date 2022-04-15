from unittest.mock import patch

from calculations import scout_precision
import server

class TestScoutPrecisionCalc:
    def setup_method(self):
        self.tba_test_data = [
            {
                'match_number': 1,
                'actual_time': 1100291640,
                'comp_level': 'qm',
                'score_breakdown': {
                    'blue': {
                        'foulPoints': 8,
                        'autoTaxiPoints': 15,
                        'totalPoints': 278,
                        'endgamePoints': 6,
                    },
                    'red': {
                        'foulPoints': 10,
                        'autoTaxiPoints': 0,
                        'totalPoints': 130,
                        'endgamePoints': 15,
                    },
                },
            },
             {
                'match_number': 2,
                'actual_time': 1087511040,
                'comp_level': 'qm',
                'score_breakdown': {
                    'blue': {
                        'foulPoints': 0,
                        'autoTaxiPoints': 0,
                        'totalPoints': 100,
                        'endgamePoints': 25,
                    },
                    'red': {
                        'foulPoints': 10,
                        'autoTaxiPoints': 0,
                        'totalPoints': 130,
                        'endgamePoints': 4
                    },
                },
            },
            {
                'match_number': 3,
                'actual_time': None,
                'comp_level': 'qm',
                'score_breakdown': None
            },
        ]
        self.scout_tim_test_data = [
            # Match 1
            {
                'scout_name': 'ALISON LIN',
                'team_number': 1678,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 5,
                'auto_low_balls': 0,
                'tele_high_balls': 9,
                'tele_low_balls': 2,
            },
            {
                'scout_name': 'NATHAN MILLS',
                'team_number': 1678,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 4,
                'auto_low_balls': 0,
                'tele_high_balls': 10,
                'tele_low_balls': 2,
            },
            {
                'scout_name': 'KATHY LI',
                'team_number': 4414,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 3,
                'auto_low_balls': 1,
                'tele_high_balls': 8,
                'tele_low_balls': 4,
            },
            {
                'scout_name': 'KATE UNGER',
                'team_number': 589,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 0,
                'auto_low_balls': 0,
                'tele_high_balls': 1,
                'tele_low_balls': 2,
            },
            {
                'scout_name': 'NITHMI JAYASUNDARA',
                'team_number': 589,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 0,
                'auto_low_balls': 0,
                'tele_high_balls': 2,
                'tele_low_balls': 2,
            },
            {
                'scout_name': 'RAY FABIONAR',
                'team_number': 589,
                'match_number': 1,
                'alliance_color_is_red': True,
                'auto_high_balls': 0,
                'auto_low_balls': 0,
                'tele_high_balls': 0,
                'tele_low_balls': 3,
            },
            # Match 2
            {
                'scout_name': 'NATHAN MILLS',
                'team_number': 1678,
                'match_number': 2,
                'alliance_color_is_red': False,
                'auto_high_balls': 3,
                'auto_low_balls': 0,
                'tele_high_balls': 14,
                'tele_low_balls': 0,
            },
            {
                'scout_name': 'KATHY LI',
                'team_number': 4414,
                'match_number': 2,
                'alliance_color_is_red': False,
                'auto_high_balls': 4,
                'auto_low_balls': 1,
                'tele_high_balls': 8,
                'tele_low_balls': 3,
            },
            {
                'scout_name': 'KATE UNGER',
                'team_number': 589,
                'match_number': 2,
                'alliance_color_is_red': False,
                'auto_high_balls': 0,
                'auto_low_balls': 0,
                'tele_high_balls': 1,
                'tele_low_balls': 2,
            },
        ]

        with patch('server.Server.ask_calc_all_data', return_value=False):
            self.test_server = server.Server()
        self.test_calc = scout_precision.ScoutPrecisionCalc(self.test_server)

    def test___init__(self):
        assert self.test_calc.watched_collections == ['unconsolidated_totals']
        assert self.test_calc.server == self.test_server

    def test_find_updated_scouts(self):
        self.test_server.db.delete_data('unconsolidated_totals')
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents('unconsolidated_totals', [{'scout_name': 'REED WANG', 'other': 9}, {'scout_name': 'NATHAN MILLS'}])
        assert sorted(self.test_calc.find_updated_scouts()) == sorted(['REED WANG', 'NATHAN MILLS'])
        self.test_calc.update_timestamp()
        self.test_server.db.update_document('unconsolidated_totals', {'other': 1}, {'scout_name': 'NATHAN MILLS'})
        assert self.test_calc.find_updated_scouts() == ['NATHAN MILLS']

    def test_get_tba_aim_score(self):
        assert self.test_calc.get_tba_aim_score(1, False, self.tba_test_data) == 249
        assert self.test_calc.get_tba_aim_score(1, True, self.tba_test_data) == 105
        assert self.test_calc.get_tba_aim_score(3, False, self.tba_test_data) == None
        assert self.test_calc.get_tba_aim_score(3, True, self.tba_test_data) == None

    def test_get_scout_tim_score(self):
        required = self.test_calc.sim_schema['calculations']['sim_precision']['requires']
        self.test_server.db.delete_data('unconsolidated_totals')
        with patch('utils.log_warning') as log_patch:
            self.test_calc.get_scout_tim_score('RAY FABIONAR', 2, required)
        log_patch.assert_called_with('No data from Scout RAY FABIONAR in Match 2')
        self.test_server.db.insert_documents('unconsolidated_totals', self.scout_tim_test_data)
        assert self.test_calc.get_scout_tim_score('ALISON LIN', 1, required) == 40
        assert self.test_calc.get_scout_tim_score('NITHMI JAYASUNDARA', 1, required) == 6
        assert self.test_calc.get_scout_tim_score('NATHAN MILLS', 2, required) == 40

    def test_get_aim_scout_scores(self):
        self.test_server.db.delete_data('unconsolidated_totals')
        self.test_server.db.insert_documents('unconsolidated_totals', self.scout_tim_test_data)
        required = self.test_calc.sim_schema['calculations']['sim_precision']['requires']
        assert self.test_calc.get_aim_scout_scores(1, True, required
        ) == {
            1678: {'ALISON LIN': 40, 'NATHAN MILLS': 38},
            4414: {'KATHY LI': 34},
            589: {'KATE UNGER': 4, 'NITHMI JAYASUNDARA': 6, 'RAY FABIONAR': 3}
        }
        assert self.test_calc.get_aim_scout_scores(2, False, required
        ) == {
            1678: {'NATHAN MILLS': 40},
            4414: {'KATHY LI': 37},
            589: {'KATE UNGER': 4}
        }    

    def test_get_aim_scout_avg_errors(self):
        with patch('utils.log_warning') as log_patch:
            assert self.test_calc.get_aim_scout_avg_errors({1678: {'KATHY LI': 9, 'RAY FABIONAR': 7}, 589: {'NITHMI JAYASUNDARA': 17}}, 100, 1, True) == {}
        log_patch.assert_called_with('Missing scout data for Match 1, Alliance is Red: True')
        aim_scout_scores = {
            1678: {'ALISON LIN': 40, 'NATHAN MILLS': 38},
            4414: {'KATHY LI': 34},
            589: {'KATE UNGER': 4, 'NITHMI JAYASUNDARA': 6, 'RAY FABIONAR': 3}
        }
        assert self.test_calc.get_aim_scout_avg_errors(aim_scout_scores, 105, 1, True
        ) == {
                'ALISON LIN': 26.666666666666668,
                'NATHAN MILLS': 28.666666666666668,
                'KATHY LI': 27.666666666666668,
                'KATE UNGER': 28,
                'NITHMI JAYASUNDARA': 26,
                'RAY FABIONAR': 29
            }

    def test_calc_sim_precision(self):
        self.test_server.db.insert_documents('unconsolidated_totals', self.scout_tim_test_data)
        with patch('calculations.scout_precision.ScoutPrecisionCalc.get_aim_scout_avg_errors', return_value={}):
            assert self.test_calc.calc_sim_precision(self.scout_tim_test_data[1], self.tba_test_data) == {}
        assert self.test_calc.calc_sim_precision(self.scout_tim_test_data[0], self.tba_test_data) == {'sim_precision': -8.222222222222221}

    def test_calc_scout_precision(self):
        assert self.test_calc.calc_scout_precision([{'scout_name': 'REED WANG'}]) == {}
        test_data = [
            {'scout_name': 'KATHY LI', 'sim_precision': 0.5, 'match_number': 1},
            {'scout_name': 'KATHY LI', 'sim_precision': 0, 'match_number': 2},
            {'scout_name': 'KATHY LI', 'sim_precision': -1, 'match_number': 3},
            {'scout_name': 'KATHY LI', 'sim_precision': 0.7243, 'match_number': 4},
            {'scout_name': 'KATHY LI', 'sim_precision': 5, 'match_number': 5},
        ]
        assert self.test_calc.calc_scout_precision(test_data) == {'scout_precision': 1.0448600000000001}

    def test_update_sim_precision_calcs(self):
        self.test_server.db.insert_documents('unconsolidated_totals', self.scout_tim_test_data)
        expected_updates = [
            {
                'scout_name': 'ALISON LIN',
                'match_number': 1,
                'team_number': 1678,
                'sim_precision': 5
            }
        ]
        with patch('data_transfer.tba_communicator.tba_request', return_value=self.tba_test_data), patch(
            'calculations.scout_precision.ScoutPrecisionCalc.calc_sim_precision', return_value={'sim_precision': 5}):
            updates = self.test_calc.update_sim_precision_calcs([{'scout_name': 'ALISON LIN', 'match_number': 1}])
            # Remove timestamp field since it's difficult to test, figure out later
            updates[0].pop('timestamp')
            assert updates == expected_updates

    def test_update_scout_precision_calcs(self):
        with patch('calculations.scout_precision.ScoutPrecisionCalc.calc_scout_precision', return_value={'scout_precision': 0.39}):
            assert self.test_calc.update_scout_precision_calcs(['REED WANG']) == [{'scout_name': 'REED WANG', 'scout_precision': 0.39}]

    def test_run(self):
        expected_sim_precision = [
            {
                'scout_name': 'ALISON LIN',
                'match_number': 1,
                'team_number': 1678,
                'sim_precision': -8.222222222222221
            },
            {
                'scout_name': 'NATHAN MILLS',
                'match_number': 1,
                'team_number': 1678,
                'sim_precision': -10.222222222222221
            },
            {
                'scout_name': 'KATHY LI',
                'match_number': 1,
                'team_number': 4414,
                'sim_precision': -9.22222222222222
            },
            {
                'scout_name': 'KATE UNGER',
                'match_number': 1,
                'team_number': 589,
                'sim_precision': -9.555555555555555
            }
        ]
        expected_scout_precision = [
            {
                'scout_name': 'ALISON LIN',
                'scout_precision': 8.222222222222221
            },
            {
                'scout_name': 'NATHAN MILLS',
                'scout_precision': 4.111111111111111
            },
            {
                'scout_name': 'KATHY LI',
                'scout_precision': 3.61111111111111
            },
            {
                'scout_name': 'KATE UNGER',
                'scout_precision': 3.7777777777777777
            },
            {
                'scout_name': 'NITHMI JAYASUNDARA',
                'scout_precision': 7.555555555555555
            },
            {
                'scout_name': 'RAY FABIONAR',
                'scout_precision': 10.555555555555555
            },
        ]
        self.test_server.db.delete_data('unconsolidated_totals')
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents('unconsolidated_totals', self.scout_tim_test_data)
        with patch('data_transfer.tba_communicator.tba_request', return_value=self.tba_test_data):
            self.test_calc.run()
        sim_precision_result = self.test_server.db.find('sim_precision')
        scout_precision_result = self.test_server.db.find('scout_precision')
        for document in sim_precision_result:
            document.pop('_id')
            # Remove timestamp field since it's difficult to test, figure out later
            document.pop('timestamp')
        for document in expected_sim_precision:
            assert document in sim_precision_result
        for document in scout_precision_result:
            document.pop('_id')
            assert document in expected_scout_precision
