import requests
import statsapi
from box import Box

BASE_URL = "https://statsapi.mlb.com/api/v1/"


class Player:
    def __init__(self, box: Box):
        self.id = box.person.id
        self.full_name = box.person.fullName
        self.position = Position(box.position)
        self.stats_all = self.get_player_stats(self.id)
        self.stats_hit = self.stats_all.get("hitting")
        self.stats_hit_adv = self.stats_all.get("hitting_adv")
        self.stats_field = self.stats_all.get("fielding")
        self.stats_field_adv = self.stats_all.get("fielding_adv")
        self.stats_pitch = self.stats_all.get("pitching")
        self.stats_pitch_adv = self.stats_all.get("pitching_adv")
        self.error = None
        self.obr = self._get_obr()
        self.sp = self._get_speed()
        self.hr = None
        self.cht = self._get_cht()
        self.sac = self._get_sac()
        self.inj = self._get_inj()
        self.single_inf = None
        self.single7 = None
        self.single8 = None
        self.single9 = None
        self.double7 = None
        self.double8 = None
        self.double9 = None
        self.triple8 = None
        self.hr = None
        self.k = None
        self.bb = None
        self.hbp = None
        self.out = self._get_card_numbers()
        self.bd = {"double": None, "triple": None, "hr": None}
        self.cd = None
        self.arm = self._get_arm()

    def __repr__(self):
        return f"{self.full_name} {self.stats_all}"

    def get(self, url):
        r = requests.get(url)
        if r.status_code not in [200, 201]:
            raise ValueError(f"Request failed. Status Code: {r.status_code}.")
        else:
            return r.json()

    def _fetch_stats(
        self,
        player_id,
        group="hitting%2Cfielding%2Cpitching",
        season=2016,
        stat_type="seasonAdvanced",
    ):
        url = BASE_URL + f"people/{player_id}/"
        url += f"stats?stats={stat_type}"
        url += f"&group={group}"
        url += f"&season={season}"
        return self.get(url)

    def _fetch_adv_player_stats(self, player_id, season=2016):
        return self._fetch_stats(
            player_id, stat_type="seasonAdvanced", season=season
        ).get("stats")

    def _fetch_player_stats(self, player_id, season=2016):
        return self._fetch_stats(player_id, stat_type="season", season=season).get(
            "stats"
        )

    def get_player_stats(self, player_id, season=2016):
        player_stats = self._fetch_player_stats(player_id, season)
        player_stats_adv = self._fetch_adv_player_stats(player_id, season)
        all_stats = dict()
        if player_stats is None and player_stats_adv is None:
            print(f"No stat found for {self.full_name}")
            return {}
        for r in player_stats:
            r = Box(r)
            stat_name = r.group.displayName
            combined_stats = r.splits
            if stat_name == "hitting" and len(combined_stats) > 2:
                # played for more than one team grab the team they ended with
                # Ordered by team -- last index is combined
                # 2nd to last is team they ended with
                stats_value = combined_stats[-2]
            elif stat_name == "fielding" and len(combined_stats) > 2:
                # played for more than one position
                # TODO figure out how to handle multiple positions
                stats_value = combined_stats[0]
            else:
                stats_value = combined_stats[0]["stat"]
            all_stats[stat_name] = stats_value
        for r in player_stats_adv:
            r = Box(r)
            stat_name = r.group.displayName + "_adv"
            combined_stats = r.splits
            if stat_name == "hitting" and len(combined_stats) > 2:
                # played for more than one team grab the team they ended with
                # Ordered by team -- last index is combined
                # 2nd to last is team they ended with
                stats_value = r.splits[0].stats[-2]
            elif stat_name == "fielding" and len(combined_stats) > 2:
                # played for more than one position
                # TODO figure out how to handle multiple positions
                stats_value = combined_stats[0].stat
            else:
                stats_value = combined_stats[0].stat

            # if stat_type == 'hitting':
            #     stats_value['batSide'] = person_results['batSide']['code']
            # if stat_type == 'pitching':
            #     stats_value['throws'] = person_results['pitchHand']['code']
            all_stats[stat_name] = stats_value
        return all_stats

    def _get_obr(self):
        scoring_rate = self._get_scoring_rate()
        if scoring_rate > 0.45:
            return "A"
        elif scoring_rate > 0.35:
            return "B"
        elif scoring_rate > 0.25:
            return "C"
        elif scoring_rate > 0.15:
            return "D"
        else:
            return "E"

    def _get_speed(self):
        if self.stats_hit is not None:
            try:
                steals = float(self.stats_hit.get("stolenBasePercentage", 0.0))
            except ValueError:
                steals = 0.0
            # print(f'{self}:{steals}')
            if steals >= 0.7:
                return "A"
            elif steals >= 0.5:
                return "B"
            elif steals >= 0.3:
                return "C"
            elif steals >= 0.1:
                return "D"
            else:
                return "E"
        else:
            return None

    def _get_scoring_rate(self):
        scoring_rate = 0.0
        if self.stats_hit is not None:
            times_on_base = (
                self.stats_hit.get("hits", 0)
                + self.stats_hit.get("baseOnBalls", 0)
                + self.stats_hit.get("hitByPitch", 0)
                + self.stats_hit.get("intentionalWalks", 0)
            )
            try:
                runs_scored = self.stats_hit.get("runs", 0)
                scoring_rate = runs_scored / times_on_base
            except ZeroDivisionError:
                return scoring_rate
            return scoring_rate
        return scoring_rate

    def _get_inj(self):
        if self.stats_hit is None:
            return None
        games_played = self.stats_hit.get("gamesPlayed", 162)
        if self.cht == "P":
            games_played *= 3.5
        games_missed = 162 - games_played
        if games_missed == 0:
            return 0
        elif games_missed == 1:
            return 1
        elif 2 <= games_missed <= 3:
            return 2
        elif 4 <= games_missed <= 5:
            return 3
        elif 6 <= games_missed <= 10:
            return 4
        elif 11 <= games_missed <= 20:
            return 5
        elif 21 <= games_missed <= 30:
            return 6
        elif 31 <= games_missed <= 80:
            return 7
        elif 81 <= games_missed <= 162:
            return 8

    def _get_cht(self):
        if self.stats_hit is None:
            return None
        if self.position.name == "Pitcher":
            return "P"
        hrs = self.stats_hit.get("homeRuns", 0)
        url = BASE_URL + f"people/{self.id}"
        r = self.get(url).get("people")[0]
        bat_side = r.get("batSide")["code"]
        if hrs >= 15:
            batter_type = "P"
        else:
            batter_type = "N"
        return bat_side + batter_type

    def _get_arm(self):
        if self.stats_pitch is None:
            return None
        return self.stats_pitch.get("throws")

    def _get_sac(self):
        if self.stats_hit is None:
            return "DD"
        sac_bunts = self.stats_hit.get("sacBunts", 0)
        if sac_bunts >= 8:
            return "AA"
        elif 5 <= sac_bunts <= 7:
            return "BB"
        elif 2 <= sac_bunts <= 4:
            return "CC"
        else:
            return "DD"

    def _get_card_numbers(self):
        plate_appearances = self.stats_hit.get("plateAppearances")
        if plate_appearances is None:
            print(
                f"{self.full_name} had 0 plate appearances."
                f" No hitting card will be made"
            )
            return
        eval_factor = self.stats_hit.get("plateAppearances") / 128
        hrs = self.stats_hit.get("homeRuns", 0)
        triples = self.stats_hit.get("triples", 0)
        doubles = self.stats_hit.get("doubles", 0)
        singles = self.stats_hit.get("hits", 0) - (hrs + triples + doubles)
        strikeouts = self.stats_hit.get("strikeOuts", 0)
        walks = self.stats_hit.get("basOnBalls", 0) + self.stats_hit.get(
            "intentionalWalks", 0
        )
        hbp = self.stats_hit.get("hitByPitch", 0)
        singles_num = round(singles * eval_factor - 11.0)
        next_num = 11
        if singles_num > 1:
            self.single_inf = next_num
            singles_num -= 1
            next_num += 1
        (equal_increment, remainder) = divmod(singles_num, 3)
        if remainder > 0:
            pull_side = self.cht[0]
            if pull_side == "R":
                next_num += equal_increment + remainder
                self.single7 = next_num
                next_num += equal_increment
                self.single8 = next_num
                next_num += equal_increment
                self.single9 = next_num
            elif pull_side == "L":
                next_num += equal_increment + remainder
                self.single7 = next_num
                next_num += equal_increment
                self.single8 = next_num
                next_num += equal_increment
                self.single9 = next_num

        doubles_num = round(doubles * eval_factor)
        triples_num = round(triples * eval_factor)
        hrs_num = round(hrs * eval_factor)
        strikeouts_num = round(strikeouts * eval_factor)
        walks_num = round(walks * eval_factor - 7.0)
        hpb_num = round(hbp * eval_factor)

        return 0


class Position:
    def __init__(self, box: Box):
        self.code = box.code
        self.name = box.name
        self.type = box.type
        self.abbreviation = box.abbreviation
