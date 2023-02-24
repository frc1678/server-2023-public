from unittest.mock import patch
import pytest

from calculations import sim_precision
import server


class TestSimPrecisionCalc:
    def setup_method(self):
        self.tba_test_data = [
            {
                "match_number": 1,
                "actual_time": 1100291640,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "foulPoints": 8,
                        "autoMobilityPoints": 15,
                        "autoGamePiecePoints": 12,
                        "teleopGamePiecePoints": 40,
                        "autoCommunity": {
                            "B": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cube",
                                "Cone",
                            ],
                        },
                        "teleopCommunity": {
                            "B": [
                                "Cone",
                                "Cube",
                                "None",
                                "Cone",
                                "Cube",
                                "Cube",
                                "Cube",
                                "Cube",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "Cone",
                                "Cube",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "Cone",
                                "Cube",
                                "Cone",
                                "None",
                                "None",
                                "None",
                                "Cone",
                                "Cube",
                                "Cone",
                            ],
                        },
                    },
                    "red": {
                        "foulPoints": 10,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 6,
                        "teleopGamePiecePoints": 63,
                        "autoCommunity": {
                            "B": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cone",
                            ],
                        },
                        "teleopCommunity": {
                            "B": [
                                "Cone",
                                "Cube",
                                "Cube",
                                "Cone",
                                "Cube",
                                "Cube",
                                "Cube",
                                "Cube",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "Cone",
                                "Cone",
                                "Cube",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                            ],
                        },
                    },
                },
            },
            {
                "match_number": 2,
                "actual_time": 1087511040,
                "comp_level": "qm",
                "score_breakdown": {
                    "blue": {
                        "foulPoints": 0,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 6,
                        "teleopGamePiecePoints": 80,
                        "autoCommunity": {
                            "B": [
                                "None",
                                "None",
                                "Cone",
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cube",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                        },
                        "teleopCommunity": {
                            "B": [
                                "Cone",
                                "Cube",
                                "None",
                                "None",
                                "Cube",
                                "Cube",
                                "None",
                                "None",
                                "None",
                            ],
                            "M": [
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                            ],
                            "T": [
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                                "Cone",
                                "Cube",
                                "Cone",
                            ],
                        },
                    },
                    "red": {
                        "foulPoints": 10,
                        "autoMobilityPoints": 0,
                        "autoGamePiecePoints": 4,
                        "teleopGamePiecePoints": 20,
                        "autoCommunity": {
                            "B": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cube",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                        },
                        "teleopCommunity": {
                            "B": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cube",
                                "None",
                                "None",
                                "None",
                                "None",
                            ],
                            "M": [
                                "None",
                                "None",
                                "None",
                                "Cone",
                                "None",
                                "Cone",
                                "None",
                                "None",
                                "None",
                            ],
                            "T": [
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "None",
                                "Cone",
                                "None",
                                "Cone",
                            ],
                        },
                    },
                },
            },
            {
                "match_number": 3,
                "actual_time": None,
                "comp_level": "qm",
                "score_breakdown": None,
            },
        ]
        self.scout_tim_test_data = [
            # Match 1
            {
                "scout_name": "ALISON LIN",
                "team_number": "1678",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 1,
                "tele_cube_high": 0,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 0,
                "auto_cone_mid": 2,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 0,
                "tele_cone_low": 2,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 1,
            },
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 1,
                "tele_cube_high": 0,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 0,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 3,
                "tele_cone_mid": 1,
                "tele_cone_low": 0,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 1,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 3,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 0,
                "tele_cone_low": 0,
                "intakes_low_row": 1,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 1,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 0,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 1,
                "tele_cone_low": 0,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            {
                "scout_name": "NITHMI JAYASUNDARA",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 1,
                "tele_cone_low": 0,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            {
                "scout_name": "RAY FABIONAR",
                "team_number": "589",
                "match_number": 1,
                "alliance_color_is_red": True,
                "auto_cube_high": 1,
                "auto_cube_mid": 1,
                "auto_cube_low": 0,
                "tele_cube_high": 0,
                "tele_cube_mid": 0,
                "tele_cube_low": 2,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 0,
                "tele_cone_low": 0,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            # Match 2
            {
                "scout_name": "NATHAN MILLS",
                "team_number": "1678",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 0,
                "auto_cone_mid": 1,
                "auto_cone_low": 0,
                "tele_cone_high": 1,
                "tele_cone_mid": 0,
                "tele_cone_low": 4,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            {
                "scout_name": "KATHY LI",
                "team_number": "4414",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 1,
                "tele_cube_mid": 0,
                "tele_cube_low": 4,
                "auto_cone_high": 1,
                "auto_cone_mid": 0,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 2,
                "tele_cone_low": 1,
                "intakes_low_row": 1,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
            {
                "scout_name": "KATE UNGER",
                "team_number": "589",
                "match_number": 2,
                "alliance_color_is_red": False,
                "auto_cube_high": 0,
                "auto_cube_mid": 0,
                "auto_cube_low": 0,
                "tele_cube_high": 2,
                "tele_cube_mid": 0,
                "tele_cube_low": 1,
                "auto_cone_high": 0,
                "auto_cone_mid": 1,
                "auto_cone_low": 0,
                "tele_cone_high": 0,
                "tele_cone_mid": 2,
                "tele_cone_low": 5,
                "intakes_low_row": 0,
                "intakes_mid_row": 0,
                "intakes_high_row": 0,
            },
        ]

        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = server.Server()
        self.test_calc = sim_precision.SimPrecisionCalc(self.test_server)

    def test___init__(self):
        assert self.test_calc.watched_collections == ["unconsolidated_totals"]
        assert self.test_calc.server == self.test_server

    def test_get_tba_aim_score(self):
        assert self.test_calc.get_tba_aim_score(1, False, self.tba_test_data) == (52, {})
        assert self.test_calc.get_tba_aim_score(1, True, self.tba_test_data) == (69, {})
        assert self.test_calc.get_tba_aim_score(3, False, self.tba_test_data) == (None, {})
        assert self.test_calc.get_tba_aim_score(3, True, self.tba_test_data) == (None, {})

    def test_get_scout_tim_score(self, caplog):
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.get_scout_tim_score("RAY FABIONAR", 2, required)
        assert ["No data from Scout RAY FABIONAR in Match 2"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        assert self.test_calc.get_scout_tim_score("ALISON LIN", 1, required) == 24
        assert self.test_calc.get_scout_tim_score("NITHMI JAYASUNDARA", 1, required) == 21
        assert self.test_calc.get_scout_tim_score("NATHAN MILLS", 2, required) == 29

    def test_get_scout_intake_row(self, caplog):
        intakes = self.test_calc.sim_schema["calculations"]["sim_precision"]["intakes"]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        self.test_calc.get_scout_tim_score("RAY FABIONAR", 2, intakes)
        assert ["No data from Scout RAY FABIONAR in Match 2"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        assert self.test_calc.get_scout_intake_row("ALISON LIN", 1, intakes) == {
            "intakes_low_row": 0,
            "intakes_mid_row": 0,
            "intakes_high_row": 1,
        }
        assert self.test_calc.get_scout_intake_row("KATHY LI", 2, intakes) == {
            "intakes_low_row": 1,
            "intakes_mid_row": 0,
            "intakes_high_row": 0,
        }
        assert self.test_calc.get_scout_intake_row("KATHY LI", 1, intakes) == {
            "intakes_low_row": 1,
            "intakes_mid_row": 0,
            "intakes_high_row": 0,
        }

    def test_get_empty_auto_nodes(self):
        assert (
            self.test_calc.get_empty_auto_nodes(self.tba_test_data[0]["score_breakdown"]["blue"])
            == {}
        )
        assert (
            self.test_calc.get_empty_auto_nodes(self.tba_test_data[0]["score_breakdown"]["red"])
            == {}
        )
        assert self.test_calc.get_empty_auto_nodes(
            self.tba_test_data[1]["score_breakdown"]["blue"]
        ) == {"intakes_low_row": 2}
        assert self.test_calc.get_empty_auto_nodes(
            self.tba_test_data[1]["score_breakdown"]["red"]
        ) == {"intakes_mid_row": 1}

    def test_get_aim_scout_scores(self):
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        intakes = self.test_calc.sim_schema["calculations"]["sim_precision"]["intakes"]
        assert self.test_calc.get_aim_scout_scores(1, True, required, intakes) == (
            {
                "1678": {"ALISON LIN": 24, "NATHAN MILLS": 25},
                "4414": {"KATHY LI": 29},
                "589": {"KATE UNGER": 21, "NITHMI JAYASUNDARA": 21, "RAY FABIONAR": 20},
            },
            {
                "1678": {
                    "ALISON LIN": {
                        "intakes_high_row": 1,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    },
                    "NATHAN MILLS": {
                        "intakes_high_row": 1,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    },
                },
                "4414": {
                    "KATHY LI": {"intakes_high_row": 0, "intakes_low_row": 1, "intakes_mid_row": 0}
                },
                "589": {
                    "KATE UNGER": {
                        "intakes_high_row": 0,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    },
                    "NITHMI JAYASUNDARA": {
                        "intakes_high_row": 0,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    },
                    "RAY FABIONAR": {
                        "intakes_high_row": 0,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    },
                },
            },
        )
        assert self.test_calc.get_aim_scout_scores(2, False, required, intakes) == (
            {
                "1678": {"NATHAN MILLS": 29},
                "4414": {"KATHY LI": 27},
                "589": {"KATE UNGER": 32},
            },
            {
                "1678": {
                    "NATHAN MILLS": {
                        "intakes_high_row": 0,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    }
                },
                "4414": {
                    "KATHY LI": {"intakes_high_row": 0, "intakes_low_row": 1, "intakes_mid_row": 0}
                },
                "589": {
                    "KATE UNGER": {
                        "intakes_high_row": 0,
                        "intakes_low_row": 0,
                        "intakes_mid_row": 0,
                    }
                },
            },
        )

    def test_get_aim_scout_avg_errors(self, caplog):
        assert (
            self.test_calc.get_aim_scout_avg_errors(
                {
                    "1678": {"KATHY LI": 9, "RAY FABIONAR": 7},
                    "589": {"NITHMI JAYASUNDARA": 17},
                },
                100,
                1,
                True,
                {
                    "1678": {
                        "KATHY LI": {
                            "intakes_high_row": 0,
                            "intakes_low_row": 0,
                            "intakes_mid_row": 0,
                        },
                        "RAY FABIONAR": {
                            "intakes_high_row": 0,
                            "intakes_low_row": 0,
                            "intakes_mid_row": 0,
                        },
                    },
                    "589": {
                        "NITHMI JAYASUNDARA": {
                            "intakes_high_row": 0,
                            "intakes_low_row": 0,
                            "intakes_mid_row": 0,
                        }
                    },
                },
                {},
            )
            == {}
        )
        assert ["Missing scout data for Match 1, Alliance is Red: True"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        aim_scout_scores = {
            "1678": {"ALISON LIN": 49, "NATHAN MILLS": 47},
            "4414": {"KATHY LI": 45},
            "589": {"KATE UNGER": 41, "NITHMI JAYASUNDARA": 40, "RAY FABIONAR": 33},
        }
        aim_scout_intakes = {
            "1678": {
                "ALISON LIN": {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0},
                "NATHAN MILLS": {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0},
            },
            "4414": {
                "KATHY LI": {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0}
            },
            "589": {
                "KATE UNGER": {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0},
                "NITHMI JAYASUNDARA": {
                    "intakes_high_row": 0,
                    "intakes_low_row": 0,
                    "intakes_mid_row": 0,
                },
                "RAY FABIONAR": {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0},
            },
        }
        empty_auto_nodes = {}
        assert self.test_calc.get_aim_scout_avg_errors(
            aim_scout_scores, 134, 1, True, aim_scout_intakes, empty_auto_nodes
        ) == {
            "ALISON LIN": 2.0,
            "NATHAN MILLS": 4.0,
            "KATHY LI": 3.0,
            "KATE UNGER": 0.0,
            "NITHMI JAYASUNDARA": 1.0,
            "RAY FABIONAR": 8.0,
        }

    def test_get_adjusted_tba_score(self):
        aim_intakes = [
            {"intakes_high_row": 0, "intakes_low_row": 0, "intakes_mid_row": 0},
            {"intakes_high_row": 1, "intakes_low_row": 0, "intakes_mid_row": 0},
            {"intakes_high_row": 0, "intakes_low_row": 1, "intakes_mid_row": 0},
        ]
        empty_auto_nodes = [{}, {"intakes_high_row": 1}, {}]
        assert self.test_calc.get_adjusted_tba_score(20, aim_intakes[0], empty_auto_nodes[0]) == 20
        assert self.test_calc.get_adjusted_tba_score(20, aim_intakes[1], empty_auto_nodes[1]) == 26
        assert self.test_calc.get_adjusted_tba_score(20, aim_intakes[2], empty_auto_nodes[2]) == 22

    def test_calc_sim_precision(self):
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        with patch(
            "calculations.sim_precision.SimPrecisionCalc.get_aim_scout_avg_errors",
            return_value={},
        ):
            assert (
                self.test_calc.calc_sim_precision(self.scout_tim_test_data[1], self.tba_test_data)
                == {}
            )
        assert self.test_calc.calc_sim_precision(
            self.scout_tim_test_data[3], self.tba_test_data
        ) == {"sim_precision": -0.2777777777777777}

    def test_update_sim_precision_calcs(self):
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        expected_updates = [
            {
                "scout_name": "ALISON LIN",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": 5,
            }
        ]
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_test_data,
        ), patch(
            "calculations.sim_precision.SimPrecisionCalc.calc_sim_precision",
            return_value={"sim_precision": 5},
        ):
            updates = self.test_calc.update_sim_precision_calcs(
                [{"scout_name": "ALISON LIN", "match_number": 1}]
            )
            # Remove timestamp field since it's difficult to test, figure out later
            updates[0].pop("timestamp")
            assert updates == expected_updates

    def test_run(self):
        expected_sim_precision = [
            {
                "scout_name": "ALISON LIN",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": -1.1111111111111114,
            },
            {
                "scout_name": "NATHAN MILLS",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": -0.11111111111111123,
            },
            {
                "scout_name": "KATHY LI",
                "match_number": 1,
                "team_number": "4414",
                "sim_precision": -0.6111111111111112,
            },
            {
                "scout_name": "KATE UNGER",
                "match_number": 1,
                "team_number": "589",
                "sim_precision": -0.2777777777777777,
            },
        ]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.update_timestamp()
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        with patch(
            "data_transfer.tba_communicator.tba_request",
            return_value=self.tba_test_data,
        ):
            self.test_calc.run()
        sim_precision_result = self.test_server.db.find("sim_precision")
        for document in sim_precision_result:
            document.pop("_id")
            # Remove timestamp field since it's difficult to test, figure out later
            document.pop("timestamp")
        for document in expected_sim_precision:
            assert document in sim_precision_result
