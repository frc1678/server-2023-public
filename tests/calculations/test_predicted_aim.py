from calculations import predicted_aim
from unittest.mock import patch
import server


class TestPredictedAimCalc:
    def setup_method(self, method):
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
                'predicted_score': 422.58142857142855,
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
                'predicted_score': 422.58142857142855,
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
                'predicted_score': 422.58142857142855,
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
                'predicted_score': 422.58142857142855,
                'predicted_rp1': 1.0,
                'predicted_rp2': 1.0,
            },
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            auto_balls_low=30.2,
            auto_balls_outer=10.5,
            auto_balls_inner=7.8,
            tele_balls_low=5.0,
            tele_balls_outer=19.4,
            tele_balls_inner=10.6,
            auto_line_success_rate=2.4,
            rotation_success_rate=1,
            position_success_rate=0,
            climb_success_rate=2.1,
            park_success_rate=0.5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
            {
                'team_number': 1678,
                'auto_avg_balls_low': 4.5,
                'auto_avg_balls_high': 6.7,
                'tele_avg_balls_low': 3.3,
                'tele_avg_balls_high': 20.8,
                'tele_cp_rotation_successes': 3,
                'tele_cp_position_successes': 1,
                'matches_played': 8,
            },
            {
                'team_number': 1533,
                'auto_avg_balls_low': 9.7,
                'auto_avg_balls_high': 5.9,
                'tele_avg_balls_low': 2.7,
                'tele_avg_balls_high': 21.5,
                'tele_cp_rotation_successes': 1,
                'tele_cp_position_successes': 0,
                'matches_played': 7,
            },
            {
                'team_number': 7229,
                'auto_avg_balls_low': 8.5,
                'auto_avg_balls_high': 7.1,
                'tele_avg_balls_low': 3.8,
                'tele_avg_balls_high': 16.4,
                'tele_cp_rotation_successes': 0,
                'tele_cp_position_successes': 0,
                'matches_played': 7,
            },
            {
                'team_number': 2468,
                'auto_avg_balls_low': 8.5,
                'auto_avg_balls_high': 7.1,
                'tele_avg_balls_low': 3.8,
                'tele_avg_balls_high': 16.4,
                'tele_cp_rotation_successes': 0,
                'tele_cp_position_successes': 0,
                'matches_played': 7,
            },
        ]
        self.tba_team = [
            {
                'team_number': 1678,
                'auto_high_balls_percent_inner': 0.4,
                'tele_high_balls_percent_inner': 0.6,
                'climb_all_successes': 7,
                'park_successes': 1,
                'auto_line_successes': 8,
            },
            {
                'team_number': 1533,
                'auto_high_balls_percent_inner': 0.3,
                'tele_high_balls_percent_inner': 0.7,
                'climb_all_successes': 4,
                'park_successes': 2,
                'auto_line_successes': 7,
            },
            {
                'team_number': 7229,
                'auto_high_balls_percent_inner': 0.1,
                'tele_high_balls_percent_inner': 0.9,
                'climb_all_successes': 2,
                'park_successes': 5,
                'auto_line_successes': 5,
            },
            {
                'team_number': 2468,
                'auto_high_balls_percent_inner': 0.1,
                'tele_high_balls_percent_inner': 0.9,
                'climb_all_successes': 2,
                'park_successes': 5,
                'auto_line_successes': 5,
            },
        ]
        self.tba_match_data = [
            {
                'match_number': 1,
                'score_breakdown': {
                    'blue': {
                        'shieldEnergizedRankingPoint': True,
                        'shieldOperationalRankingPoint': True,
                        'totalPoints': 278,
                    },
                    'red': {
                        'shieldEnergizedRankingPoint': False,
                        'shieldOperationalRankingPoint': True,
                        'totalPoints': 320,
                    },
                },
                'winning_alliance': 'red',
            },
            {
                'match_number': 3,
                'score_breakdown': {
                    'blue': {
                        'shieldEnergizedRankingPoint': None,
                        'shieldOperationalRankingPoint': None,
                        'totalPoints': None,
                    },
                    'red': {
                        'shieldEnergizedRankingPoint': None,
                        'shieldOperationalRankingPoint': None,
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

    def test_calculate_stage_contribution(self):
        assert self.test_calc.calculate_stage_contribution(self.full_predicted_values) == 44

    def test_calculate_predicted_balls_score(self):
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[0], self.tba_team[0]
        )
        assert self.blank_predicted_values.auto_balls_low == 4.5
        assert self.blank_predicted_values.auto_balls_outer == 4.02
        assert self.blank_predicted_values.auto_balls_inner == 2.68
        assert self.blank_predicted_values.tele_balls_low == 3.3
        assert self.blank_predicted_values.tele_balls_outer == 8.32
        assert self.blank_predicted_values.tele_balls_inner == 12.48
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[1], self.tba_team[1]
        )
        assert self.blank_predicted_values.auto_balls_low == 14.2
        assert self.blank_predicted_values.auto_balls_outer == 8.149999999999999
        assert self.blank_predicted_values.auto_balls_inner == 4.45
        assert self.blank_predicted_values.tele_balls_low == 6.0
        assert self.blank_predicted_values.tele_balls_outer == 14.770000000000001
        assert self.blank_predicted_values.tele_balls_inner == 27.53
        self.test_calc.calculate_predicted_balls_score(
            self.blank_predicted_values, self.obj_team[2], self.tba_team[2]
        )
        assert self.blank_predicted_values.auto_balls_low == 22.7
        assert self.blank_predicted_values.auto_balls_outer == 14.539999999999999
        assert self.blank_predicted_values.auto_balls_inner == 5.16
        assert self.blank_predicted_values.tele_balls_low == 9.8
        assert self.blank_predicted_values.tele_balls_outer == 16.410000000000001
        assert self.blank_predicted_values.tele_balls_inner == 42.29

    def test_calculate_predicted_panel_score(self):
        self.test_calc.calculate_predicted_panel_score(
            self.blank_predicted_values, self.obj_team[1]
        )
        assert self.blank_predicted_values.rotation_success_rate == 1
        assert self.blank_predicted_values.position_success_rate == 0

    def test_calculate_predicted_alliance_score(self):
        assert (
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values, self.obj_team, self.tba_team, [1678, 1533, 7229]
            )
            == 422.58142857142855
        )

    def test_calculate_climb_rp(self):
        assert self.test_calc.calculate_predicted_climb_rp(self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_climb_rp(self.full_predicted_values) == 1

    def test_calculate_stage_rp(self):
        assert self.test_calc.calculate_predicted_stage_rp(self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_stage_rp(self.full_predicted_values) == 1

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
