import pytest

from unittest.mock import Mock, mock_open, patch

from calculations.base_calculations import BaseCalculations
from server import Server


@pytest.mark.clouddb
class TestBaseCalculations:
    def setup_method(self, method):
        with patch("server.Server.ask_calc_all_data", return_value=False):
            self.test_server = Server()
        self.base_calc = BaseCalculations(self.test_server)
        with patch("server.Server.ask_calc_all_data", return_value=True):
            self.test_server_all_data = Server()
        self.base_calc_all_data = BaseCalculations(self.test_server_all_data)

    def test__init__(self):
        assert self.base_calc.server == self.test_server
        assert self.base_calc.oplog == self.test_server.db.client.local.oplog.rs
        assert self.base_calc.calc_all_data == False
        assert self.base_calc_all_data.calc_all_data == True
        assert self.base_calc.watched_collections == NotImplemented

    def test_update_timestamp(self):
        self.test_server.db.insert_documents("test", {"a": 1})
        self.base_calc.update_timestamp()
        op = self.base_calc.oplog.find_one({"op": "i", "o.a": 1})
        assert self.base_calc.timestamp >= op["ts"]

    def test_entries_since_last(self):
        self.base_calc.watched_collections = ["testing"]
        self.test_server.db.insert_documents("testing", {"c": 1})
        self.base_calc.update_timestamp()
        self.test_server.db.insert_documents("testing", [{"a": 1}, {"a": 2}, {"a": 3}])
        self.test_server.db.delete_data("testing", {"a": 1})
        self.test_server.db.update_document("testing", {"b": 2}, {"a": 2})
        # There were 5 operations after the timestamp update:
        # 3 inserts, 1 deletion, 1 update
        assert len(self.base_calc.entries_since_last()) == 5
        for entry in self.base_calc.entries_since_last():
            assert entry["ts"] > self.base_calc.timestamp
            assert entry["op"] in ["d", "i", "u"]
            assert "c" not in entry["o"].keys()
        # Test with calc_all_data as True
        self.base_calc_all_data.watched_collections = ["testing1"]
        self.test_server_all_data.db.insert_documents("testing1", {"c": 1})
        self.base_calc_all_data.update_timestamp()
        self.test_server_all_data.db.insert_documents("testing1", [{"a": 1}, {"a": 2}, {"a": 3}])
        self.test_server_all_data.db.delete_data("testing1", {"a": 1})
        self.test_server_all_data.db.update_document("testing1", {"b": 2}, {"a": 2})
        assert len(self.base_calc_all_data.entries_since_last()) == 3
        contains_first_insert = False
        for entry in self.base_calc_all_data.entries_since_last():
            assert entry["op"] == None
            if "c" in entry["o"].keys():
                contains_first_insert = True
        assert contains_first_insert == True

    def test_get_updated_teams(self):
        self.base_calc.update_timestamp()
        self.base_calc.watched_collections = ["test"]
        self.test_server.db.insert_documents(
            "test",
            [
                {"team_number": "0"},
                {"useless": 0},
                {"team_number": "1", "useless": 0},
            ],
        )
        assert sorted(self.base_calc.get_updated_teams()) == ["0", "1"]
        self.base_calc.update_timestamp()
        self.test_server.db.update_document("test", {"team_number": "1"}, {"useless": 1})
        assert self.base_calc.get_updated_teams() == ["1"]
        # Test with calc_all_data as True
        self.base_calc_all_data.watched_collections = ["test1"]
        self.test_server_all_data.db.insert_documents("test1", {"team_number": "6"})
        self.base_calc_all_data.update_timestamp()
        self.test_server_all_data.db.insert_documents("test1", {"team_number": "8"})
        # Cast to set to disregard order of items
        assert set(self.base_calc_all_data.get_updated_teams()) == set(["8", "6"])

    def test_avg(self):
        # Test if there is no input
        assert 0 == BaseCalculations.avg("")
        # Test average with no weights
        assert 2 == BaseCalculations.avg([1, 2, 3])
        # Test error if there are a different amount of weights than numbers
        with pytest.raises(ValueError) as num_error:
            BaseCalculations.avg([1, 2], [3, 4, 5])
        assert "Weighted average expects one weight for each number." in str(num_error)
        # Test average with weights
        assert 1 == BaseCalculations.avg([1, 3], [2.0, 0.0])

    def test_get_aim_list(self):
        test_json = """
        {
            "1": 
            {
                "teams": [
                    {"number": "88", "color": "blue"}, 
                    {"number": "2342", "color": "blue"},
                    {"number": "157", "color": "blue"}, 
                    {"number": "4041", "color": "red"},
                    {"number": "1153", "color": "red"},
                    {"number": "2370", "color": "red"}
                ]
            }
        }
        """
        expected_aim_list = [
            {
                "match_number": 1,
                "alliance_color": "B",
                "team_list": ["88", "2342", "157"],
            },
            {
                "match_number": 1,
                "alliance_color": "R",
                "team_list": ["4041", "1153", "2370"],
            },
        ]
        with patch("calculations.base_calculations.open", mock_open(read_data=test_json)):
            assert BaseCalculations.get_aim_list() == expected_aim_list

    def test_get_teams_list(self, caplog):
        with patch("calculations.base_calculations.open", mock_open(read_data="[1,2,3]")) as _:
            assert BaseCalculations.get_teams_list() == [1, 2, 3]

        def f(*args):
            raise FileNotFoundError

        with patch("calculations.base_calculations.open", Mock(side_effect=f)):
            assert BaseCalculations.get_teams_list() == []
            # Assert that the FileNotFoundError was logged
            assert len([rec.message for rec in caplog.records if rec.levelname == "ERROR"]) == 1
