import csv

import pymongo

import utils


class BaseCalculations:
    def __init__(self, server):
        self.server = server
        self.oplog = self.server.oplog
        self.update_timestamp()
        self.watched_collections = NotImplemented  # Calculations should override this attribute
        self.teams_list = self._get_teams_list()

    def update_timestamp(self):
        """Updates the timestamp to the most recent oplog entry timestamp"""
        last_op = self.oplog.find({}).sort('ts', pymongo.DESCENDING).limit(1)
        self.timestamp = last_op.next()['ts']

    def entries_since_last(self):
        """Find changes in watched collections since the last update_timestamp()

        This checks the oplog for insert ('i'), delete ('d'), or update ('u') operations that have
        been performed on the watched collections and returns a PyMongo cursor object
        with the query results.
        """
        return self.oplog.find(
            {
                'ts': {'$gt': self.timestamp},
                'op': {'$in': ['i', 'd', 'u']},
                'ns': {'$in': [f'{self.server.db.name}.{c}' for c in self.watched_collections]},
            }
        )

    def find_team_list(self) -> list:
        """Returns a list of team numbers that appear in watched_collections"""
        teams = set()
        for entry in self.entries_since_last():
            # Prevents error from not having a team num
            if "team_number" in entry["o"].keys():
                teams.add(entry["o"]["team_number"])
            # If the doc was updated, need to manually find the document
            elif entry['op'] == 'u':
                if (
                    query := self.server.db.find(entry['ns'].split('.')[-1])
                ) != [] and 'team_number' in query[0].keys():
                    teams.add(query[0]['team_number'])
        return list(teams)

    @staticmethod
    def avg(nums, weights=None, default=0):
        """Calculates the average of a list of numeric types.

        If the optional parameter weights is given, calculates a weighted average
        weights should be a list of floats. The length of weights must be the same as the length of nums
        default is the value returned if nums is an empty list
        """
        if len(nums) == 0:
            return default
        if weights is None:
            # Normal (not weighted) average
            return sum(nums) / len(nums)
        if len(nums) != len(weights):
            raise ValueError(f'Weighted average expects one weight for each number.')
        weighted_sum = sum([num * weight for num, weight in zip(nums, weights)])
        return weighted_sum / sum(weights)

    @staticmethod
    def modes(data: list) -> list:
        """Returns the most frequently occurring items in the given list"""
        if len(data) == 0:
            return []
        # Create a dictionary of things to how many times they occur in the list
        frequencies = {}
        for item in data:
            frequencies[item] = 1 + frequencies.get(item, 0)
        # How many times each mode occurs in nums:
        max_occurrences = max(frequencies.values())
        return [item for item, frequency in frequencies.items() if frequency == max_occurrences]

    @staticmethod
    def _get_teams_list():
        try:
            with open('data/team_list.csv') as f:
                reader = csv.reader(f)
                return [int(n) for n in next(reader)]
        except FileNotFoundError:
            utils.log_error('base_calculations: data/team_list.csv not found')
            return []
