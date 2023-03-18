from unittest.mock import patch
import pytest
from utils import dict_near_in, dict_near, read_schema

from calculations import sim_precision
import server


class TestSimPrecisionCalc:
    @staticmethod
    def near(num1, num2, max_diff=0.01) -> bool:
        return abs(num1 - num2) <= max_diff

    @staticmethod
    def dict_near(dict1, dict2, max_diff=0.01) -> bool:
        if len(dict1) != len(dict2):
            return False
        for field in dict1:
            if field not in dict2:
                return False
            if not (isinstance(dict1[field], float) and isinstance(dict2[field], float)):
                if not dict1[field] == dict2[field]:
                    return False
            else:
                if not TestSimPrecisionCalc.near(dict1[field], dict2[field], max_diff):
                    return False
        return True

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

    def test_get_scout_tim_score(self, caplog):
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_calc.get_scout_tim_score("RAY FABIONAR", 2, required)
        assert ["No data from Scout RAY FABIONAR in Match 2"] == [
            rec.message for rec in caplog.records if rec.levelname == "WARNING"
        ]
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        assert self.test_calc.get_scout_tim_score("ALISON LIN", 1, required) == 19
        assert self.test_calc.get_scout_tim_score("NITHMI JAYASUNDARA", 1, required) == 21
        assert self.test_calc.get_scout_tim_score("NATHAN MILLS", 2, required) == 29

    def test_get_aim_scout_scores(self):
        self.test_server.db.delete_data("unconsolidated_totals")
        self.test_server.db.insert_documents("unconsolidated_totals", self.scout_tim_test_data)
        required = self.test_calc.sim_schema["calculations"]["sim_precision"]["requires"]
        assert self.test_calc.get_aim_scout_scores(1, True, required) == {
            "1678": {"ALISON LIN": 19, "NATHAN MILLS": 20},
            "4414": {"KATHY LI": 27},
            "589": {"KATE UNGER": 21, "NITHMI JAYASUNDARA": 21, "RAY FABIONAR": 20},
        }
        assert self.test_calc.get_aim_scout_scores(2, False, required) == {
            "1678": {"NATHAN MILLS": 29},
            "4414": {"KATHY LI": 25},
            "589": {"KATE UNGER": 32},
        }

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
        assert self.test_calc.get_aim_scout_avg_errors(aim_scout_scores, 134, 1, True) == {
            "ALISON LIN": 2.0,
            "NATHAN MILLS": 4.0,
            "KATHY LI": 3.0,
            "KATE UNGER": 0.0,
            "NITHMI JAYASUNDARA": 1.0,
            "RAY FABIONAR": 8.0,
        }

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
        sim_precision_result = self.test_calc.calc_sim_precision(
            self.scout_tim_test_data[3], self.tba_test_data
        )

        fields_to_keep = {"sim_precision"}
        # Remove fields we are not testing
        for field in list(sim_precision_result.keys()):
            if field not in fields_to_keep:
                sim_precision_result.pop(field)

        assert dict_near(
            sim_precision_result, {"sim_precision": -0.2777777777777777 - 0.6666666666666666}
        )

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

    def test_get_tba_value(self):
        required = {
            "something_that_should_be_ignored": {
                "weight": 1000,
                "calculation": [
                    ["autoCommunity", "T", "+2*count=Cube"],
                    ["foulPoints", "-2*value"],
                    ["+1*constant"],
                ],
            },
            "another_thing_that_doesn't_matter": {
                "weight": -0,
                "calculation": ["teleopCommunity", "B", "+1*count=Cone"],
            },
        }
        assert self.test_calc.get_tba_value(self.tba_test_data, required, 1, False) == -11

    def test_get_tba_datapoint_value(self):
        command = [
            ["autoCommunity", "T", "+2*count=Cube"],
            ["foulPoints", "-2*value"],
            ["+1*constant"],
        ]
        assert (
            self.test_calc.get_tba_datapoint_value(
                self.tba_test_data[0]["score_breakdown"]["blue"], command
            )
            == -13
        )

    def test_run(self):
        expected_sim_precision = [
            {
                "scout_name": "ALISON LIN",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": -1.1111111111111114 - 0.6666666666666666,
            },
            {
                "scout_name": "NATHAN MILLS",
                "match_number": 1,
                "team_number": "1678",
                "sim_precision": -0.11111111111111123 - 0.6666666666666666,
            },
            {
                "scout_name": "KATHY LI",
                "match_number": 1,
                "team_number": "4414",
                "sim_precision": -0.6111111111111112 - 0.6666666666666666,
            },
            {
                "scout_name": "KATE UNGER",
                "match_number": 1,
                "team_number": "589",
                "sim_precision": -0.2777777777777777 - 0.6666666666666666,
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
        fields_to_keep = {"sim_precision", "scout_name", "match_number", "team_number"}
        schema = read_schema("schema/calc_sim_precision_schema.yml")
        calculations = schema["calculations"]
        for document in sim_precision_result:
            for calculation in calculations:
                assert calculation in document
            assert "_id" in document
            assert "timestamp" in document
            # Remove fields we are not testing
            for field in list(document.keys()):
                if field not in fields_to_keep:
                    document.pop(field)

        for document in expected_sim_precision:
            assert dict_near_in(document, sim_precision_result)
