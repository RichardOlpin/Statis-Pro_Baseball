import statsapi


class Player:
    def __init__(self, **kwargs):
        self.id = kwargs['person']['id']
        self.first_name = kwargs['person']['fullName'].split()[0]
        self.last_name = kwargs['person']['fullName'].split()[1:]
        self.position = Position(**kwargs['position'])
        self.bats = None
        self.error = None
        self.obr = self.get_obr()
        self.sp = None
        self.hr = None
        self.cd = None
        self.sac = None
        self.inj = None
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
        self.arm = None
        self.stats_all = self.get_player_stats(self.id)
        self.stats_hitting = self.stats_all.get('hitting')
        self.stats_fielding = self.stats_all.get('fielding')
        self.stats_pitching = self.stats_all.get('pitching')

    @classmethod
    def get_player_stats(cls, player_id, group='[hitting,pitching,fielding]',
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
            all_stats[stat_type] = stats_value
        return all_stats



class Position:
    def __init__(self, **kwargs):
        self.code = kwargs['code']
        self.name = kwargs['name']
        self.type = kwargs['type']
        self.abbreviation = kwargs['abbreviation']

