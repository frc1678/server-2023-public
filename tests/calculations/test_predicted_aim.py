from calculations import predicted_aim
from unittest.mock import patch
import server


class TestPredictedAimCalc:
    def setup_method(self, method):
        with patch('server.Server.ask_calc_all_data', return_value=False):
            self.test_server = server.Server()
        self.test_calc = predicted_aim.PredictedAimCalc(self.test_server)
        self.aims_list = [
            {'match_number': 1, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]},
            {'match_number': 1, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]},
            {'match_number': 2, 'alliance_color': 'R', 'team_list': [1678, 1533, 1690]},
            {'match_number': 2, 'alliance_color': 'B', 'team_list': [254, 1323, 973]},
            {'match_number': 3, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]},
            {'match_number': 3, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]},
        ]
        self.filtered_aims_list = [
            {'match_number': 1, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]},
            {'match_number': 1, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]},
            {'match_number': 3, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]},
            {'match_number': 3, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]},
        ]
        self.expected_results = [
            {
                'match_number': 1,
                'alliance_color_is_red': True,
                'has_actual_data': True,
                'actual_score': 320,
                'actual_rp1': 0.0,
                'actual_rp2': 1.0,
                'predicted_score': 243.3107142857143,
                'predicted_rp1': 1.0,
                'predicted_rp2': 1.0,
            },
            {
                'match_number': 1,
                'alliance_color_is_red': False,
                'has_actual_data': True,
                'actual_score': 278,
                'actual_rp1': 1.0,
                'actual_rp2': 1.0,
                'predicted_score': 241.79642857142858,
                'predicted_rp1': 1.0,
                'predicted_rp2': 1.0,
            },
            {
                'match_number': 3,
                'alliance_color_is_red': True,
                'has_actual_data': False,
                'actual_score': 0,
                'actual_rp1': 0.0,
                'actual_rp2': 0.0,
                'predicted_score': 243.3107142857143,
                'predicted_rp1': 1.0,
                'predicted_rp2': 1.0,
            },
            {
                'match_number': 3,
                'alliance_color_is_red': False,
                'has_actual_data': False,
                'actual_score': 0,
                'actual_rp1': 0.0,
                'actual_rp2': 0.0,
                'predicted_score': 241.79642857142858,
                'predicted_rp1': 1.0,
                'predicted_rp2': 1.0,
            },
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            auto_balls_low=30.2,
            auto_balls_high=10.5,
            tele_balls_low=5.0,
            tele_balls_high=19.4,
            auto_line_success_rate=2.4,
            low_rung_success_rate=1.2,
            mid_rung_success_rate=0.9,
            high_rung_success_rate=0.3, 
            traversal_rung_success_rate=0.5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
            {
                'team_number': 1678,
                'auto_avg_lows': 4.5,
                'auto_avg_balls_high': 7.5,
                'auto_avg_balls_total': 12.0,
                'tele_avg_lows': 3.3,
                'tele_avg_balls_high': 16.1,
                "tele_avg_balls_total": 19.4,
                'low_rung_successes': 1,
                'mid_rung_successes': 1,
                'high_rung_successes': 3,
                'traversal_rung_successes': 3,
                'matches_played': 8,
            },
            {
                'team_number': 1533,
                'auto_avg_lows': 3.7,
                'auto_avg_balls_high': 8.2,
                'auto_avg_balls_total': 11.9,
                'tele_avg_lows': 2.7,
                'tele_avg_balls_high': 27.4,
                "tele_avg_balls_total": 30.1,
                'low_rung_successes': 1,
                'mid_rung_successes': 0,
                'high_rung_successes': 6,
                'traversal_rung_successes': 0,
                'matches_played': 7,
            },
            {
                'team_number': 7229,
                'auto_avg_lows': 3.5,
                'auto_avg_balls_high': 6.4,
                'auto_avg_balls_total': 9.9,
                'tele_avg_lows': 3.8,
                'tele_avg_balls_high': 3.9,
                "tele_avg_balls_total": 7.7,
                'low_rung_successes': 0,
                'mid_rung_successes': 2,
                'high_rung_successes': 0,
                'traversal_rung_successes': 0,
                'matches_played': 7,
            },
            {
                'team_number': 2468,
                'auto_avg_lows': 1.5,
                'auto_avg_balls_high': 3.2,
                'auto_avg_balls_total': 4.7,
                'tele_avg_lows': 10.8,
                'tele_avg_balls_high': 1.4,
                "tele_avg_balls_total": 12.2,
                'low_rung_successes': 0,
                'mid_rung_successes': 0,
                'high_rung_successes': 0,
                'traversal_rung_successes': 7,
                'matches_played': 7,
            },
        ]
        self.tba_team = [
            {
                'team_number': 1678,
                'auto_line_successes': 8,
            },
            {
                'team_number': 1533,
                'auto_line_successes': 7,
            },
            {
                'team_number': 7229,
                'auto_line_successes': 5,
            },
            {
                'team_number': 2468,
                'auto_line_successes': 5,
            },
        ]
        self.tba_match_data = [
            {
                'match_number': 1,
                'score_breakdown': {
                    'blue': {
                        'cargoBonusRankingPoint': True,
                        'hangarBonusRankingPoint': True,
                        'totalPoints': 278,
                    },
                    'red': {
                        'cargoBonusRankingPoint': False,
                        'hangarBonusRankingPoint': True,
                        'totalPoints': 320,
                    },
                },
                'winning_alliance': 'red',
            },
            {
                'match_number': 3,
                'score_breakdown': {
                    'blue': {
                        'cargoBonusRankingPoint': None,
                        'hangarBonusRankingPoint': None,
                        'totalPoints': None,
                    },
                    'red': {
                        'cargoBonusRankingPoint': None,
                        'hangarBonusRankingPoint': None,
                        'totalPoints': None,
                    },
                },
                'winning_alliance': '',
            },
        ]
        self.test_server.db.insert_documents('obj_team', self.obj_team)
        self.test_server.db.insert_documents('tba_team', self.tba_team)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ['obj_team', 'tba_team']
        assert self.test_calc.server == self.test_server

    def test_calculate_predicted_quintet_success(self):
        assert self.test_calc.calculate_predicted_quintet_success(self.obj_team) == 18

    def test_calculate_predicted_balls_score(self):
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[0]
        )
        assert self.blank_predicted_values.auto_balls_low == 4.5
        assert self.blank_predicted_values.auto_balls_high == 7.5
        assert self.blank_predicted_values.tele_balls_low == 3.3
        assert self.blank_predicted_values.tele_balls_high == 16.1
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[1]
        )
        assert self.blank_predicted_values.auto_balls_low == 8.2
        assert self.blank_predicted_values.auto_balls_high == 15.7
        assert self.blank_predicted_values.tele_balls_low == 6.0
        assert self.blank_predicted_values.tele_balls_high == 43.5
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[2]
        )
        assert self.blank_predicted_values.auto_balls_low == 11.7
        assert round(self.blank_predicted_values.auto_balls_high, 1) == 22.1
        assert self.blank_predicted_values.tele_balls_low == 9.8
        assert self.blank_predicted_values.tele_balls_high == 47.4

    def test_calculate_predicted_alliance_score(self):
        assert (
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values, self.obj_team, self.tba_team, [1678, 1533, 7229]
            )
            == 243.3107142857143
        )

    def test_calculate_climb_rp(self):
        assert self.test_calc.calculate_predicted_climb_rp(self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_climb_rp(self.full_predicted_values) == 1

    def test_calculate_ball_rp(self):
        print(self.blank_predicted_values)
        assert self.test_calc.calculate_predicted_ball_rp(self.obj_team, self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_ball_rp(self.obj_team, self.full_predicted_values) == 1

    def test_get_actual_values(self):
        with patch('data_transfer.tba_communicator.tba_request', return_value=self.tba_match_data):
            assert self.test_calc.get_actual_values(
                {'match_number': 1, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]}
            ) == {
                'has_actual_data': True,
                'actual_score': 320,
                'actual_rp1': 0.0,
                'actual_rp2': 1.0,
            }
            assert self.test_calc.get_actual_values(
                {'match_number': 1, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]}
            ) == {
                'has_actual_data': True,
                'actual_score': 278,
                'actual_rp1': 1.0,
                'actual_rp2': 1.0,
            }
            assert self.test_calc.get_actual_values(
                {'match_number': 3, 'alliance_color': 'R', 'team_list': [1678, 1533, 7229]}
            ) == {
                'has_actual_data': False,
                'actual_score': 0,
                'actual_rp1': 0.0,
                'actual_rp2': 0.0,
            }
            assert self.test_calc.get_actual_values(
                {'match_number': 3, 'alliance_color': 'B', 'team_list': [1678, 1533, 2468]}
            ) == {
                'has_actual_data': False,
                'actual_score': 0,
                'actual_rp1': 0.0,
                'actual_rp2': 0.0,
            }

    def test_filter_aims_list(self):
        assert (
            self.test_calc.filter_aims_list(self.obj_team, self.tba_team, self.aims_list)
            == self.filtered_aims_list
        )

    def test_update_predicted_aim(self):
        with patch('data_transfer.tba_communicator.tba_request', return_value=self.tba_match_data):
            assert self.test_calc.update_predicted_aim(self.aims_list) == self.expected_results

    def test_run(self):
        self.test_server.db.delete_data('obj_team')
        self.test_server.db.delete_data('tba_team')
        self.test_server.db.insert_documents('obj_team', self.obj_team)
        self.test_server.db.insert_documents('tba_team', self.tba_team)
        with patch(
            'calculations.predicted_aim.PredictedAimCalc._get_aim_list', return_value=self.aims_list
        ), patch('data_transfer.tba_communicator.tba_request', return_value=self.tba_match_data):
            self.test_calc.run()
        result = self.test_server.db.find('predicted_aim')
        assert len(result) == 4
        for document in result:
            del document['_id']
            assert document in self.expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            self.expected_results.remove(document)
