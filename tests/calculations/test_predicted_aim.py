from calculations import predicted_aim
from unittest.mock import patch
import server
import pytest


class TestPredictedAimCalc:
    @staticmethod
    def near(num1, num2, max_diff=0.01) -> bool:
        return abs(num1 - num2) <= max_diff

    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = predicted_aim.PredictedAimCalc(self.test_server)
        self.aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 2,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "1690"],
            },
            {
                "match_number": 2,
                "alliance_color": "B",
                "team_list": ["254", "1323", "973"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
        ]
        self.filtered_aims_list = [
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
        ]
        self.expected_updates = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "has_actual_data": True,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "predicted_score": 271.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 268.66667,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 271.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 268.66667,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
            },
        ]
        self.expected_results = [
            {
                "match_number": 1,
                "alliance_color_is_red": True,
                "has_actual_data": True,
                "actual_score": 320,
                "actual_rp1": 0.0,
                "actual_rp2": 1.0,
                "won_match": True,
                "predicted_score": 271.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 0.98733,
            },
            {
                "match_number": 1,
                "alliance_color_is_red": False,
                "has_actual_data": True,
                "actual_score": 278,
                "actual_rp1": 1.0,
                "actual_rp2": 1.0,
                "won_match": False,
                "predicted_score": 268.66667,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 1 - 0.98733,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": True,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 271.33333,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 0.98733,
            },
            {
                "match_number": 3,
                "alliance_color_is_red": False,
                "has_actual_data": False,
                "actual_score": 0,
                "actual_rp1": 0.0,
                "actual_rp2": 0.0,
                "won_match": False,
                "predicted_score": 268.66667,
                "predicted_rp1": 0.25,
                "predicted_rp2": 1.0,
                "win_chance": 1 - 0.98733,
            },
        ]
        self.full_predicted_values = predicted_aim.PredictedAimScores(
            auto_dock_successes=0.5,
            auto_engage_successes=0.5,
            tele_engage_successes=1.5,
            tele_dock_successes=0.5,
            link=5,
        )
        self.blank_predicted_values = predicted_aim.PredictedAimScores()
        self.obj_team = [
            {
                "team_number": "1678",
                "auto_avg_cube_low": 1.0,
                "auto_avg_cone_low": 2.5,
                "auto_avg_cube_mid": 4.5,
                "auto_avg_cone_mid": 3.5,
                "auto_avg_cube_high": 7.5,
                "auto_avg_cone_high": 6.0,
                "auto_avg_cube_total": 13.0,
                "auto_avg_cone_total": 12.0,
                "tele_avg_cube_low": 3.3,
                "tele_avg_cone_low": 2.3,
                "tele_avg_cube_mid": 3.5,
                "tele_avg_cone_mid": 2.5,
                "tele_avg_cube_high": 2.2,
                "tele_avg_cone_high": 4.3,
                "tele_avg_cube_total": 9.0,
                "tele_avg_cone_total": 8.1,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 1,
                "auto_dock_percent_success": 1.0,
                "auto_dock_only_percent_success": 1.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 1,
                "tele_dock_percent_success": 0.5,
                "tele_dock_only_percent_success": 0.5,
                "tele_engage_successes": 1,
                "tele_engage_percent_success": 0.5,
                "tele_park_successes": 0,
                "tele_park_percent_success": 0.0,
            },
            {
                "team_number": "1533",
                "auto_avg_cube_low": 1.1,
                "auto_avg_cone_low": 2.6,
                "auto_avg_cube_mid": 4.6,
                "auto_avg_cone_mid": 3.6,
                "auto_avg_cube_high": 7.6,
                "auto_avg_cone_high": 6.1,
                "auto_avg_cube_total": 13.3,
                "auto_avg_cone_total": 12.3,
                "tele_avg_cube_low": 3.4,
                "tele_avg_cone_low": 2.4,
                "tele_avg_cube_mid": 3.6,
                "tele_avg_cone_mid": 2.6,
                "tele_avg_cube_high": 2.3,
                "tele_avg_cone_high": 4.4,
                "tele_avg_cube_total": 9.3,
                "tele_avg_cone_total": 8.4,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 1,
                "auto_engage_percent_success": 1.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 1,
                "tele_engage_percent_success": 0.5,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "7229",
                "auto_avg_cube_low": 1.2,
                "auto_avg_cone_low": 2.7,
                "auto_avg_cube_mid": 4.7,
                "auto_avg_cone_mid": 3.7,
                "auto_avg_cube_high": 7.7,
                "auto_avg_cone_high": 6.2,
                "auto_avg_cube_total": 13.6,
                "auto_avg_cone_total": 12.6,
                "tele_avg_cube_low": 3.5,
                "tele_avg_cone_low": 2.5,
                "tele_avg_cube_mid": 3.7,
                "tele_avg_cone_mid": 2.7,
                "tele_avg_cube_high": 2.4,
                "tele_avg_cone_high": 4.5,
                "tele_avg_cube_total": 9.6,
                "tele_avg_cone_total": 8.7,
                "auto_charge_attempts": 2,
                "auto_dock_successes": 1,
                "auto_dock_percent_success": 0.5,
                "auto_dock_only_percent_success": 0.5,
                "auto_engage_successes": 1,
                "auto_engage_percent_success": 0.5,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 1,
                "tele_dock_percent_success": 0.5,
                "tele_dock_only_percent_success": 0.5,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "2468",
                "auto_avg_cube_low": 1.1,
                "auto_avg_cone_low": 2.7,
                "auto_avg_cube_mid": 4.6,
                "auto_avg_cone_mid": 3.7,
                "auto_avg_cube_high": 7.6,
                "auto_avg_cone_high": 6.2,
                "auto_avg_cube_total": 13.3,
                "auto_avg_cone_total": 12.6,
                "tele_avg_cube_low": 3.4,
                "tele_avg_cone_low": 2.5,
                "tele_avg_cube_mid": 3.6,
                "tele_avg_cone_mid": 2.7,
                "tele_avg_cube_high": 2.3,
                "tele_avg_cone_high": 4.5,
                "tele_avg_cube_total": 9.3,
                "tele_avg_cone_total": 8.7,
                "auto_charge_attempts": 1,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 2,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 1,
                "tele_park_percent_success": 0.5,
            },
            {
                "team_number": "1000",
                "auto_avg_cube_low": 0.0,
                "auto_avg_cone_low": 0.0,
                "auto_avg_cube_mid": 0.0,
                "auto_avg_cone_mid": 0.0,
                "auto_avg_cube_high": 0.0,
                "auto_avg_cone_high": 0.0,
                "auto_avg_cube_total": 0.0,
                "auto_avg_cone_total": 0.0,
                "tele_avg_cube_low": 0.0,
                "tele_avg_cone_low": 0.0,
                "tele_avg_cube_mid": 0.0,
                "tele_avg_cone_mid": 0.0,
                "tele_avg_cube_high": 0.0,
                "tele_avg_cone_high": 0.0,
                "tele_avg_cube_total": 0.0,
                "tele_avg_cone_total": 0.0,
                "auto_charge_attempts": 0,
                "auto_dock_successes": 0,
                "auto_dock_percent_success": 0.0,
                "auto_dock_only_percent_success": 0.0,
                "auto_engage_successes": 0,
                "auto_engage_percent_success": 0.0,
                "tele_charge_attempts": 0,
                "tele_dock_successes": 0,
                "tele_dock_percent_success": 0.0,
                "tele_dock_only_percent_success": 0.0,
                "tele_engage_successes": 0,
                "tele_engage_percent_success": 0.0,
                "tele_park_successes": 0,
                "tele_park_percent_success": 0.0,
            },
        ]
        self.tba_team = [
            {
                "team_number": "1678",
            },
            {
                "team_number": "1533",
            },
            {
                "team_number": "7229",
            },
            {
                "team_number": "2468",
            },
            {
                "team_number": "1000",
            },
        ]
        self.tba_match_data = [
            {
                "match_number": 1,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 278,
                    },
                    "red": {
                        "activationBonusAchieved": False,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 320,
                    },
                },
                "post_result_time": 182,
                "winning_alliance": "red",
            },
            {
                "match_number": 1,
                "comp_level": "qf",
                "score_breakdown": {
                    "blue": {
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 300,
                    },
                    "red": {
                        "activationBonusAchieved": True,
                        "sustainabilityBonusAchieved": True,
                        "totalPoints": 400,
                    },
                },
                "post_result_time": 182,
                "winning_alliance": "red",
            },
            {
                "match_number": 3,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "activationBonusAchieved": None,
                        "sustainabilityBonusAchieved": None,
                        "totalPoints": 0,
                    },
                    "red": {
                        "activationBonusAchieved": None,
                        "sustainabilityBonusAchieved": None,
                        "totalPoints": 0,
                    },
                },
                "post_result_time": None,
                "winning_alliance": "",
            },
        ]
        self.test_server.db.insert_documents("obj_team", self.obj_team)
        self.test_server.db.insert_documents("tba_team", self.tba_team)

    def test___init__(self):
        """Test if attributes are set correctly"""
        assert self.test_calc.watched_collections == ["obj_team", "tba_team"]
        assert self.test_calc.server == self.test_server

    def test_calculate_predicted_link_score(self):
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[0])
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[1])
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[2])
        self.test_calc.calculate_predicted_link_score(self.blank_predicted_values, self.obj_team)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.link, 9)

    def test_calculate_predicted_grid_score(self):
        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[0])
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_gamepieces_low, 3.5)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_mid, 3.5)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_high, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_high, 6.0)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_gamepieces_low, 5.6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_mid, 2.5)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_high, 2.2)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_high, 4.3)

        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[1])
        assert TestPredictedAimCalc.near(
            self.blank_predicted_values.auto_gamepieces_low, 1.0 + 2.5 + 1.1 + 2.6
        )
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_mid, 6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_high, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_high, 6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_gamepieces_low, 9)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_mid, 2.6 + 2.5)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_high, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_high, 6)

        self.test_calc.calculate_predicted_grid_score(self.blank_predicted_values, self.obj_team[2])
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_gamepieces_low, 9)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_mid, 6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cube_high, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.auto_cone_high, 6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_gamepieces_low, 9)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_mid, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_mid, 6)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cube_high, 3)
        assert TestPredictedAimCalc.near(self.blank_predicted_values.tele_cone_high, 6)

    def test_calculate_predicted_alliance_score(self):
        assert TestPredictedAimCalc.near(
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1678", "1533", "7229"],
            ),
            271.33333,
        )

        try:
            self.test_calc.calculate_predicted_alliance_score(
                self.blank_predicted_values,
                self.obj_team,
                self.tba_team,
                ["1000", "1000", "1000"],
            )
        except ZeroDivisionError as exc:
            assert False, f"calculate_predicted_alliance_score has a {exc}"

    def test_calculate_predicted_link_rp(self):
        assert self.test_calc.calculate_predicted_link_rp(self.blank_predicted_values) == 0
        assert self.test_calc.calculate_predicted_link_rp(self.full_predicted_values) == 1

    def test_calculate_predicted_charge_rp(self):
        assert (
            self.test_calc.calculate_predicted_charge_rp(
                self.blank_predicted_values, self.obj_team, ["1000", "1000", "1000"]
            )
            == 0
        )
        assert (
            self.test_calc.calculate_predicted_charge_rp(
                self.full_predicted_values, self.obj_team, ["1678", "1533", "7229"]
            )
            == 0.25
        )

    def test_get_actual_values(self):
        assert self.test_calc.get_actual_values(
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": True,
            "actual_score": 320,
            "actual_rp1": 0.0,
            "actual_rp2": 1.0,
            "won_match": True,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": True,
            "actual_score": 278,
            "actual_rp1": 1.0,
            "actual_rp2": 1.0,
            "won_match": False,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 3,
                "alliance_color": "R",
                "team_list": ["1678", "1533", "7229"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": False,
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
        }
        assert self.test_calc.get_actual_values(
            {
                "match_number": 3,
                "alliance_color": "B",
                "team_list": ["1678", "1533", "2468"],
            },
            self.tba_match_data,
        ) == {
            "has_actual_data": False,
            "actual_score": 0,
            "actual_rp1": 0.0,
            "actual_rp2": 0.0,
            "won_match": False,
        }

    def test_filter_aims_list(self):
        assert (
            self.test_calc.filter_aims_list(self.obj_team, self.tba_team, self.aims_list)
            == self.filtered_aims_list
        )

    def test_update_predicted_aim(self):
        self.test_server.db.delete_data("predicted_aim")
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_match_data,
        ):
            assert self.test_calc.update_predicted_aim(self.aims_list) == self.expected_updates

    def test_calculate_predicted_win_chance(self):
        with patch("data_transfer.database.Database.find", return_value=self.expected_updates):
            assert self.test_calc.calculate_predicted_win_chance() == self.expected_results

    def test_get_predicted_win_chance(self):
        match_list = list(range(1, 6))
        aims = [
            {
                "match_number": 1,
                "predicted_score": 10,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 1,
                "predicted_score": 20,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 2,
                "predicted_score": 14,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 2,
                "predicted_score": 16,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 3,
                "predicted_score": 13,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 3,
                "predicted_score": 18,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 4,
                "predicted_score": 12,
                "has_actual_data": True,
                "won_match": True,
            },
            {
                "match_number": 4,
                "predicted_score": 11,
                "has_actual_data": True,
                "won_match": False,
            },
            {
                "match_number": 5,
                "predicted_score": 1000,
                "has_actual_data": False,
            },
            {
                "match_number": 5,
                "predicted_score": 0,
                "has_actual_data": False,
            },
        ]
        predicted_win_chance = self.test_calc.get_predicted_win_chance(match_list, aims)
        assert predicted_win_chance(-10) == 0.008404776287221662
        assert predicted_win_chance(-1) == 0.6934716286186654
        assert predicted_win_chance(0) == 0.8080157677406733
        assert predicted_win_chance(3) == 0.9644107365854077

    def test_run(self):
        self.test_server.db.delete_data("obj_team")
        self.test_server.db.delete_data("tba_team")
        self.test_server.db.delete_data("predicted_aim")
        self.test_server.db.insert_documents("obj_team", self.obj_team)
        self.test_server.db.insert_documents("tba_team", self.tba_team)
        with patch(
            "calculations.predicted_aim.PredictedAimCalc.get_aim_list",
            return_value=self.aims_list,
        ), patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_match_data,
        ):
            self.test_calc.run()
        result = self.test_server.db.find("predicted_aim")
        assert len(result) == 4
        for document in result:
            del document["_id"]
            assert document in self.expected_results
            # Removes the matching expected result to protect against duplicates from the calculation
            self.expected_results.remove(document)
