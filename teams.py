import statsapi
from player import Player

MLB_TEAMS = [t for t in statsapi.get('teams', {})['teams']
             if t['sport']['name'] == 'Major League Baseball']
ABRV_TO_ID = {t['abbreviation']: t['id'] for t in MLB_TEAMS}
ID_TO_ABRV = {t['id']: t['abbreviation'] for t in MLB_TEAMS}


cubs = statsapi.lookup_team(ABRV_TO_ID['CHC'])

cubs_2016 = statsapi.get('team_roster', {'teamId': ABRV_TO_ID['CHC'],
                                         'rosterType': 'fullSeason',
                                         'season': 2016})
cubs_players = [Player(**player) for player in cubs_2016['roster']]
