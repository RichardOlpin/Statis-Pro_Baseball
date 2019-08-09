import statsapi


class Player:
    def __init__(self, **kwargs):
        self.id = kwargs['person']['id']
        self.first_name = kwargs['person']['fullName'].split()[0]
        self.last_name = ' '.join(kwargs['person']['fullName'].split()[1:])
        self.position = Position(**kwargs['position'])
        self.stats_all = self.get_player_stats(self.id)
        self.stats_hitting = self.stats_all.get('hitting')
        self.stats_fielding = self.stats_all.get('fielding')
        self.stats_pitching = self.stats_all.get('pitching')
        self.bats = None
        self.error = None
        self.obr = self._get_obr()
        self.sp = self._get_speed()
        self.hr = None
        self.cht = self._get_cht()
        self.sac = None
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
        self.out = None
        self.bd = {'double': None,
                   'triple': None,
                   'hr': None
                   }
        self.cd = None
        self.arm = self._get_arm()

    def __repr__(self):
        return f'{self.first_name} {self.last_name} {self.stats_all}'

    def get_player_stats(self, player_id, group='[hitting,pitching,fielding]',
                         stat_type='season',
                         params=None):
        if not params:
            params = {'personId': player_id,
                      'hydrate': f'stats(group={group},type={stat_type}),currentTeam'}
        person_results = statsapi.get('person', params)['people'][0]
        all_stats = dict()
        results = person_results.get('stats')
        if results is None:
            print(f'No stats found for {self.first_name} {self.last_name}')
            return {}
        for r in results:
            stat_type = r['group']['displayName']
            stats_value = r['splits'][0]['stat']
            if stat_type == 'hitting':
                stats_value['batSide'] = person_results['batSide']['code']
            if stat_type == 'pitching':
                stats_value['throws'] = person_results['pitchHand']['code']
            all_stats[stat_type] = stats_value
        return all_stats

    def _get_obr(self):
        scoring_rate = self._get_scoring_rate()
        if scoring_rate > .45:
            return 'A'
        elif scoring_rate > .35:
            return 'B'
        elif scoring_rate > .25:
            return 'C'
        elif scoring_rate > .15:
            return 'D'
        else:
            return 'E'

    def _get_speed(self):
        if self.stats_hitting is not None:
            try:
                steals = float(self.stats_hitting.get('stolenBasePercentage', 0.0))
            except ValueError:
                steals = 0.0
            # print(f'{self}:{steals}')
            if steals >= 0.7:
                return 'A'
            elif steals >= 0.5:
                return 'B'
            elif steals >= 0.3:
                return 'C'
            elif steals >= 0.1:
                return 'D'
            else:
                return 'E'
        else:
            return None

    def _get_scoring_rate(self):
        scoring_rate = 0.0
        if self.stats_hitting is not None:
            times_on_base = self.stats_hitting.get('hits', 0) + \
                            self.stats_hitting.get('baseOnBalls', 0) +\
                            self.stats_hitting.get('hitByPitch', 0) + \
                            self.stats_hitting.get('intentionalWalks', 0)
            try:
                scoring_rate = self.stats_hitting['runs'] / times_on_base
            except ZeroDivisionError:
                return scoring_rate
            return scoring_rate
        return scoring_rate

    def _get_inj(self):
        if self.stats_hitting is None:
            return None
        games_played = self.stats_hitting.get('gamesPlayed', 162)
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
        if self.stats_hitting is None:
            return None
        if self.position.name == 'Pitcher':
            return 'P'
        hrs = self.stats_hitting['homeRuns']
        bat_side = self.stats_hitting['batSide']
        if hrs >= 15:
            batter_type = 'P'
        else:
            batter_type = 'N'
        return bat_side + batter_type

    def _get_arm(self):
        if self.stats_pitching is None:
            return None
        return self.stats_pitching.get('throws')



class Position:
    def __init__(self, **kwargs):
        self.code = kwargs['code']
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.abbreviation = kwargs['abbreviation']

