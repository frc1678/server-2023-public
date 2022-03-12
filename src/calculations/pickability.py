from calculations import base_calculations
import utils

import pymongo


class PickabilityCalc(base_calculations.BaseCalculations):
    """This class calculates pickability"""

    def __init__(self, server):
        super().__init__(server)
        self.pickability_schema = utils.read_schema('schema/calc_pickability_schema.yml')[
            'calculations'
        ]
        self.get_watched_collections()
        self.get_calc_data()

    def get_watched_collections(self):
        """Reads from the schema file to generate the correct watched collections"""
        self.watched_collections = set()
        for calc in self.pickability_schema:
            for sub_calc in self.pickability_schema[calc]['requires']:
                if '.' in sub_calc:
                    self.watched_collections.add(sub_calc.split('.')[0])
        self.watched_collections = list(self.watched_collections)

    def get_calc_data(self):
        """Produces a dictionary of a list of tuples

        e.g. {'first_pickability': [('obj_team', 'avg_ball_high')]}
        Key is the calc, each tuple represents the collection and the specific datapoint needed"""
        self.calcs = {}
        for calc_name in self.pickability_schema.keys():
            sub_calcs = []
            for sub_calc in self.pickability_schema[calc_name]['requires']:
                sub_calcs.append((sub_calc.split(".")[0], sub_calc.split('.')[1]))
            self.calcs[calc_name] = sub_calcs

    def calculate_pickability(self, team_number: int, calc_name: str, team_data: dict) -> float:
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
        for weight in self.pickability_schema[calc_name]['weights']:
            # If the weight isn't a constant number, it's a datapoint
            # Find the value of the datapoint
            if isinstance(weight, str):
                collection, datapoint = weight.split('.')
                if (data := self.server.db.find(collection, team_number=team_number)) != []:
                    weight = data[0][datapoint]
                else: 
                    weight = 0
            weights.append(weight)
        weighted_sum = sum([datapoint * weight for datapoint, weight in zip(datapoints, weights)])
        return weighted_sum

    def run(self) -> None:
        """Detects when and for which teams to calculate pickabilty"""
        # Finds oplog entries in the watched collections
        entries = self.entries_since_last()
        if entries == []:
            return
        # Stores the new pickability dictionaries
        updates = []
        for team in self.find_team_list():
            # Data that is needed to calculate pickability
            team_data = {}
            # Get each calc name and search for it in the database
            for collection in self.watched_collections:
                if (query := self.server.db.find(collection, team_number=team)) != []:
                    team_data[collection] = query[0]
                else:
                    continue

            if (first_pickability := self.calculate_pickability(team, 'first_pickability', team_data)) is None:
                utils.log_error(f'First pickability could not be calculated for team: {team}')
                continue

            if (second_pickability := self.calculate_pickability(team, 'second_pickability', team_data)) is None:
                utils.log_error(f'Second pickability could not be calculated for team: {team}')
                continue
            # Append the new pickability to the updates list
            update = {'team_number': team}
            update['first_pickability'] = first_pickability
            update['second_pickability'] = second_pickability
            updates.append(update)
        if updates:
            self.server.db.bulk_write(
                'pickability',
                [
                    pymongo.UpdateOne(
                        {'team_number': update['team_number']}, {'$set': update}, upsert=True
                    )
                    for update in updates
                ],
            )
        self.update_timestamp()
