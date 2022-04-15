#!/usr/bin/env python3
"""Calculates scout precisions to determine scout accuracy compared to TBA."""

from datetime import datetime

from calculations.base_calculations import BaseCalculations
from data_transfer import tba_communicator
import utils

class ScoutPrecisionCalc(BaseCalculations):

    def __init__(self, server):
        super().__init__(server)
        self.watched_collections = ['unconsolidated_totals']
        self.overall_schema = utils.read_schema('schema/calc_scout_precision_schema.yml')
        self.sim_schema = utils.read_schema('schema/calc_sim_precision_schema.yml')
    
    def find_updated_scouts(self):
        """Returns a list of scout names that appear in entries_since_last"""
        scouts = set()
        for entry in self.entries_since_last():
            # Prevents error from not having a team num
            if 'scout_name' in entry['o'].keys():
                scouts.add(entry['o']['scout_name'])
            # If the doc was updated, need to manually find the document
            elif entry['op'] == 'u':
                document_id = entry['o2']['_id']
                if (
                    query := self.server.db.find(entry['ns'].split('.')[-1], _id=document_id),
                ) != [] and 'scout_name' in query[0].keys():
                    scouts.add(query[0]['scout_name'])
        return list(scouts)
    
    def get_tba_aim_score(self, match_number, alliance_color_is_red, tba_match_data):
        """Gets the total cargo and climb score for an alliance in match from TBA.
        aim is a dictionary with a match number and alliance color.
        tba_match_data is the result of a TBA request for matches.
        """
        if alliance_color_is_red:
            alliance_color = 'red'
        else:
            alliance_color = 'blue'
        for match in tba_match_data:
            if (
                match['match_number'] == match_number
                and match['comp_level'] == 'qm'
                and match['score_breakdown'] != None
            ):
                score = match['score_breakdown'][alliance_color]['totalPoints']
                # Subtract foul and auto line points, which scouts don't collect
                # Also subtract climb points which may be inaccurate on TBA
                score -= match['score_breakdown'][alliance_color]['foulPoints']
                score -= match['score_breakdown'][alliance_color]['autoTaxiPoints']
                score -= match['score_breakdown'][alliance_color]['endgamePoints']
                return score
        return

    def get_scout_tim_score(self, scout, match_number, required):
        """Gets the score for a team in a match reported by a scout.
        required is the dictionary of required datapoints: point values from schema
        """
        scout_data = self.server.db.find('unconsolidated_totals', match_number=match_number, scout_name=scout)
        if scout_data == []:
            utils.log_warning(f'No data from Scout {scout} in Match {match_number}')
            return
        scout_document = scout_data[0]
        total_score = 0
        for datapoint, point_value in required.items():
            datapoint = datapoint.split('.')[1]
            total_score += (scout_document[datapoint] * point_value)
        return total_score
    
    def get_aim_scout_scores(self, match_number, alliance_color_is_red, required):
        """Gets the individual TIM scores reported by each scout for an alliance in a match.
        required is the dictionary of required datapoints: point values from schema.
        Returns a dictionary where keys are team numbers and values are dictionaries of scout name: tim score.
        """
        scores_per_team = {}
        scout_data = self.server.db.find('unconsolidated_totals', match_number=match_number, alliance_color_is_red=alliance_color_is_red)
        teams = set([document['team_number'] for document in scout_data])
        for team in teams:
            scores_per_team[team] = {}
        for document in scout_data:
            scout_tim_score = self.get_scout_tim_score(document['scout_name'], match_number, required)
            scores_per_team[document['team_number']].update({document['scout_name']: scout_tim_score})
        return scores_per_team

    def get_aim_scout_avg_errors(self, aim_scout_scores, tba_aim_score, match_number, alliance_color_is_red):
        """Gets the average error from TBA of each scout's linear combinations in an AIM."""
        if len(aim_scout_scores) < 3:
            utils.log_warning(f'Missing scout data for Match {match_number}, Alliance is Red: {alliance_color_is_red}')
            return {}
        team1_scouts =  list(aim_scout_scores.values())[0]
        team2_scouts =  list(aim_scout_scores.values())[1]
        team3_scouts =  list(aim_scout_scores.values())[2]

        all_scout_errors = {}
        for scout1, score1 in team1_scouts.items():
            scout1_errors = all_scout_errors.get(scout1, [])
            for scout2, score2 in team2_scouts.items():
                scout2_errors = all_scout_errors.get(scout2, [])
                for scout3, score3 in team3_scouts.items():
                    scout3_errors = all_scout_errors.get(scout3, [])
                    error = tba_aim_score - (score1 + score2 + score3)
                    scout1_errors.append(error)
                    scout2_errors.append(error)
                    scout3_errors.append(error)
                    all_scout_errors[scout3] = scout3_errors
                all_scout_errors[scout2] = scout2_errors
            all_scout_errors[scout1] = scout1_errors
        scout_avg_errors = {scout: self.avg(errors) for scout, errors in all_scout_errors.items()}
        return scout_avg_errors

    def calc_sim_precision(self, sim, tba_match_data):
        """Calculates the average difference between errors where the scout was part of the combination, and errors where the scout wasn't.
        sim is a scout-in-match document."""
        calculations = {}
        tba_aim_score = self.get_tba_aim_score(sim['match_number'], sim['alliance_color_is_red'], tba_match_data)
        for calculation, schema in self.sim_schema['calculations'].items():
            required = schema['requires']
            # Score reported by a specific scout for a robot in a match
            scout_tim_score = self.get_scout_tim_score(sim['scout_name'], sim['match_number'], required)
            # Get the average errors of all scouts in a match
            aim_scout_scores = self.get_aim_scout_scores(sim['match_number'], sim['alliance_color_is_red'], required)
            aim_scout_errors = self.get_aim_scout_avg_errors(aim_scout_scores, tba_aim_score, sim['match_number'], sim['alliance_color_is_red'])
            if aim_scout_errors == {}:
                continue
            # Remove the team scouted by the scout, only consider alliance partners
            aim_scout_scores.pop(sim['team_number'])
            ally1_scouts = list(aim_scout_scores.values())[0]
            ally2_scouts = list(aim_scout_scores.values())[1]
            sim_errors = []
            for scout1, ally1_score in ally1_scouts.items():
                for scout2, ally2_score in ally2_scouts.items():
                    current_combo_error = tba_aim_score - (scout_tim_score + ally1_score + ally2_score)
                    # Each aim_scout_error value represents the average error of 3 scouts, so divide by 3
                    average_partner_error = (aim_scout_errors[scout1] + aim_scout_errors[scout2]) / 3
                    error_difference = average_partner_error - current_combo_error
                    sim_errors.append(error_difference)
            calculations[calculation] = self.avg(sim_errors)
        return calculations

    def calc_scout_precision(self, scout_sims):
        """Averages all of a scout's in-match errors to get their overall error in a competition."""
        calculations = {}
        for calculation, schema in self.overall_schema['calculations'].items():
            required = schema['requires']
            datapoint = required.split('.')[1]
            all_sim_errors = []
            for document in scout_sims:
                if document.get(datapoint) is not None:
                    all_sim_errors.append(document[datapoint])
            if all_sim_errors != []:
                calculations[calculation] = abs(self.avg(all_sim_errors))
        return calculations

    def update_sim_precision_calcs(self, unconsolidated_sims):
        """Creates scout-in-match precision updates"""
        tba_match_data = tba_communicator.tba_request(f'event/{utils.TBA_EVENT_KEY}/matches')
        updates = []
        for sim in unconsolidated_sims:
            sim_data = self.server.db.find('unconsolidated_totals', **sim)[0]
            update = {}
            update['scout_name'] = sim_data['scout_name']
            update['match_number'] = sim_data['match_number']
            update['team_number'] = sim_data['team_number']
            for match in tba_match_data:
                if match['match_number'] == sim_data['match_number'] and match['comp_level'] == 'qm':
                    # Convert match timestamp from Unix time (on TBA) to human readable
                    update['timestamp'] = datetime.fromtimestamp(match['actual_time'])
                    break
            if (sim_precision := self.calc_sim_precision(sim_data, tba_match_data)) != {}:
                update.update(sim_precision)
            updates.append(update)
        return updates
    
    def update_scout_precision_calcs(self, scouts):
        """Creates overall precision updates."""
        updates = []
        for scout in scouts:
            scout_sims = self.server.db.find('sim_precision', scout_name=scout)
            update = {}
            update['scout_name'] = scout
            if (scout_precision := self.calc_scout_precision(scout_sims)) != {}:
                update.update(scout_precision)
            updates.append(update)
        return updates

    def run(self):
        entries = self.entries_since_last()
        scouts = self.find_updated_scouts()
        sims = []
        for entry in entries:
            sims.append(
                {
                    'scout_name': entry['o']['scout_name'],
                    'match_number': entry['o']['match_number']
                }
            )
        # Delete and re-insert if updating all data
        if self.calc_all_data:
            self.server.db.delete_data('sim_precision')
            self.server.db.delete_data('scout_precision')

        for update in self.update_sim_precision_calcs(sims):
            self.server.db.update_document('sim_precision', update, {'scout_name': update['scout_name'], 'match_number': update['match_number']})
        for update in self.update_scout_precision_calcs(scouts):
            self.server.db.update_document('scout_precision', update, {'scout_name': update['scout_name']})
