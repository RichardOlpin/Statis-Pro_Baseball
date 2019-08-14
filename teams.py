import statsapi
from box import Box
from player import Player

MLB_TEAMS = [
    t
    for t in statsapi.get("teams", {})["teams"]
    if t["sport"]["name"] == "Major League Baseball"
]
ABRV_TO_ID = {t["abbreviation"]: t["id"] for t in MLB_TEAMS}
ID_TO_ABRV = {t["id"]: t["abbreviation"] for t in MLB_TEAMS}


class Team:
    def __init__(self, roster):
        self.fielders = [player for player in roster if player.position.code != "1"]
        self.pitchers = [player for player in roster if player.position.code == "1"]


cubs = statsapi.lookup_team(ABRV_TO_ID["CHC"])

cubs_2016 = statsapi.get(
    "team_roster",
    {"teamId": ABRV_TO_ID["CHC"], "rosterType": "fullSeason", "season": 2016},
)
boxed_cubs_players = [Box(**player) for player in cubs_2016["roster"]]
cubs_players = [Player(player) for player in boxed_cubs_players]

CUBS = Team(cubs_players)
