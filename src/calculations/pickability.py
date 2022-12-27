from calculations import base_calculations
import utils


class PickabilityCalc(base_calculations.BaseCalculations):
    """This class calculates pickability"""

    def __init__(self, server):
        super().__init__(server)
        self.pickability_schema = utils.read_schema("schema/calc_pickability_schema.yml")[
            "calculations"
        ]
        self.get_watched_collections()
        self.get_calc_data()

    def get_watched_collections(self):
        """Reads from the schema file to generate the correct watched collections"""
        self.watched_collections = set()
        for calc in self.pickability_schema:
            for sub_calc in self.pickability_schema[calc]["requires"]:
                if "." in sub_calc:
                    self.watched_collections.add(sub_calc.split(".")[0])
        self.watched_collections = list(self.watched_collections)

    def get_calc_data(self):
        """Produces a dictionary of a list of tuples

        e.g. {'first_pickability': [('obj_team', 'avg_ball_high')]}
        Key is the calc, each tuple represents the collection and the specific datapoint needed"""
        self.calcs = {}
        for calc_name in self.pickability_schema.keys():
            sub_calcs = []
            for sub_calc in self.pickability_schema[calc_name]["requires"]:
                sub_calcs.append((sub_calc.split(".")[0], sub_calc.split(".")[1]))
            self.calcs[calc_name] = sub_calcs

    def calculate_pickability(self, team_number: str, calc_name: str, team_data: dict) -> float:
        """Calculates first and second pickability

        calc_name is which pickability to calculate (e.g. first or second)
        team_data is the data required to perform the weighted sum
        returns the weighted sum
        """
        datapoints = []  # Datapoints to avg
        for calc in self.calcs[calc_name]:  # Datapoints of first or second pickability
            if calc[0] in team_data.keys() and calc[1] in team_data[calc[0]].keys():
                datapoints.append(team_data[calc[0]][calc[1]])
            else:
                return None
        weights = []
        for weight in self.pickability_schema[calc_name]["weights"]:
            # If the weight is a dictionary, it's a datapoint
            # Key is datapoint name, value is adjustable weight
            if isinstance(weight, dict):
                for datapoint, weight_value in weight.items():
                    collection, datapoint = datapoint.split(".")
                    if (
                        data := self.server.db.find(collection, {"team_number": team_number})
                    ) != []:
                        weight = data[0][datapoint] * weight_value
                    else:
                        weight = 0
            weights.append(weight)
        weighted_sum = sum([datapoint * weight for datapoint, weight in zip(datapoints, weights)])
        return weighted_sum

    def update_pickability(self):
        """Creates updated pickability documents"""
        updates = []
        for team in self.get_updated_teams():
            # Data that is needed to calculate pickability
            team_data = {}
            # Get each calc name and search for it in the database
            for collection in self.watched_collections:
                if (query := self.server.db.find(collection, {"team_number": team})) != []:
                    team_data[collection] = query[0]
                else:
                    continue
            update = {"team_number": team}
            for calc_name in self.pickability_schema.keys():
                value = self.calculate_pickability(team, calc_name, team_data)
                if value is None:
                    utils.log_error(f"{calc_name} could not be calculated for team: {team}")
                    continue
                update[calc_name] = value
                updates.append(update)
        return updates

    def run(self) -> None:
        """Detects when and for which teams to calculate pickabilty"""
        # Finds oplog entries in the watched collections
        entries = self.entries_since_last()
        if entries == []:
            return
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data("pickability")

        for update in self.update_pickability():
            self.server.db.update_document(
                "pickability", update, {"team_number": update["team_number"]}
            )
