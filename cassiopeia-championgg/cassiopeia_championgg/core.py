from typing import Set, Union

from merakicommons.ghost import ghost_load_on
from merakicommons.container import SearchableDictionary, SearchableLazyList, searchable
from merakicommons.cache import lazy_property

from datapipelines import NotFoundError

from cassiopeia import configuration
from cassiopeia.data import Region, Role, Tier
from cassiopeia.core.common import CoreData, CassiopeiaGhost, CoreDataList, CassiopeiaLazyList, CassiopeiaObject
from cassiopeia.core.patch import Patch

from .dto import ChampionGGStatsDto, ChampionGGStatsListDto, ChampionGGMatchupDto, ChampionGGMatchupListDto


class ChampionGGStatsListData(CoreDataList):
    _dto_type = ChampionGGStatsListDto
    _renamed = {}

    @property
    def region(self) -> str:
        return self._dto["region"]


class ChampionGGMatchupListData(CoreDataList):
    _dto_type = ChampionGGMatchupListDto
    _renamed = {}

    @property
    def region(self) -> str:
        return self._dto["region"]


class ChampionGGStatsData(CoreData):
    _dto_type = ChampionGGStatsDto
    _renamed = {"championId": "id", "overallPerformanceScore": "performanceScore", "percentRolePlayed": "playRateByRole", "totalHeal": "totalHealed", "neutralMinionsKilledTeamJungle": "neutralMinionsKilledInTeamJungle", "neutralMinionsKilledEnemyJungle": "neutralMinionsKilledInEnemyJungle"}

    def __call__(self, **kwargs):
        if "elo" in kwargs:
            self.elo = kwargs.pop("elo").split(",")
        super().__call__(**kwargs)
        return self


class ChampionGGMatchupData(CoreData):
    _dto_type = ChampionGGMatchupDto
    _renamed = {}

    def __call__(self, **kwargs):
        if "elo" in kwargs:
            self.elo = kwargs.pop("elo").split(",")
        super().__call__(**kwargs)


class ChampionGGChampionData(CoreData):
    _dto_type = ChampionGGMatchupDto
    _renamed = {}

    def __call__(self, **kwargs):
        if "elo" in kwargs:
            self.elo = kwargs.pop("elo").split(",")
        super().__call__(**kwargs)


########
# Core #
########


class ChampionGGMatchupStats:
    def __init__(self, data, id):
        self.id = id
        self.twenty_to_thirty = data.get('twentyToThirty', None)
        self.wins = data.get('wins', None)
        self.winrate = data.get('winrate', None)
        self.kills = data.get('kills', None)
        self.neutral_minions_killed_team_jungle = data.get('neutralMinionsKilledTeamJungle', None)
        self.total_damage_dealt_to_champions = data.get('totalDamageDealtToChampions', None)
        self.role = data.get('role', None)
        self.assists = data.get('assists', None)
        self.ten_to_twenty = data.get('tenToTwenty', None)
        self.thirty_to_end = data.get('thirtyToEnd', None)
        self.zero_to_ten = data.get('zeroToTen', None)
        self.gold_earned = data.get('goldEarned', None)
        self.killing_sprees = data.get('killingSprees', None)
        self.minions_killed = data.get('minionsKilled', None)
        self.deaths = data.get('deaths', None)
        self.weighted_score = data.get('weighedScore', None)
        self.delta_twenty_to_thirty = data.get('deltatwentyToThirty', None)
        self.delta_wins = data.get('deltawins', None)
        self.delta_winrate = data.get('deltawinrate', None)
        self.delta_kills = data.get('deltakills', None)
        self.delta_neutral_minions_killed_team_jungle = data.get('deltaneutralMinionsKilledTeamJungle', None)
        self.delta_total_damage_dealt_to_champions = data.get('deltatotalDamageDealtToChampions', None)
        self.delta_assists = data.get('deltaassists', None)
        self.delta_ten_to_twenty = data.get('deltatenToTwenty', None)
        self.delta_thirty_to_end = data.get('deltathirtyToEnd', None)
        self.delta_zero_to_ten = data.get('deltazeroToTen', None)
        self.delta_gold_earned = data.get('deltagoldEarned', None)
        self.delta_killing_sprees = data.get('deltakillingSprees', None)
        self.delta_minions_killed = data.get('deltaminionsKilled', None)
        self.delta_deaths = data.get('deltadeaths', None)
        self.delta_weighted_score = data.get('deltaweighedScore', None)
        from cassiopeia import Champion
        self.champion = Champion(id=self.id, region="NA")  # TODO give correct version


@searchable({str: ["enemy.champion"]})
class ChampionGGMatchup(CassiopeiaGhost):
    _data_types = {ChampionGGMatchupData}

    def __init__(self, id: int = None, champion: int = None, patch: Patch = None, elo: Set[str] = None, region: Union[Region, str] = None):
        if region is None:
            region = configuration.settings.default_region
        if region is not None and not isinstance(region, Region):
            region = Region(region)
        if elo is None:
            elo = "PLATINUM_DIAMOND_MASTER_CHALLENGER"
        kwargs = {}
        if region is not None:
            kwargs["region"] = region
        if patch is not None:
            kwargs["patch"] = patch.name
        if id is not None:
            kwargs["id"] = id
        if elo is not None:
            kwargs["elo"] = elo
        super().__init__(**kwargs)
        self._patch = patch

    def __get_query__(self):
        return {"id": self.id, "patch": self.patch.name, "elo": "_".join(self.elo)}

    @lazy_property
    def region(self) -> Region:
        return Region(self._data[ChampionGGMatchupData].region)

    @property
    def elo(self) -> Set[str]:
        return self._data[ChampionGGMatchupData].elo

    @property
    def patch(self) -> Patch:
        return self._patch

    @property
    def me(self) -> ChampionGGMatchupStats:
        data = self._data[ChampionGGMatchupData]
        if data.champ1_id == self._hack:
            return ChampionGGMatchupStats(data.champ1, id=data.champ1_id)
        else:
            return ChampionGGMatchupStats(data.champ2, id=data.champ2_id)

    @property
    def enemy(self) -> ChampionGGMatchupStats:
        data = self._data[ChampionGGMatchupData]
        if data.champ1_id == self._hack:
            return ChampionGGMatchupStats(data.champ2, id=data.champ2_id)
        else:
            return ChampionGGMatchupStats(data.champ1, id=data.champ1_id)

    @property
    def winrate(self) -> float:
        total = self.me.wins + self.enemy.wins
        return self.me.wins / total

    @property
    def nmatches(self) -> int:
        return self.me.wins + self.enemy.wins


class ChampionGGMatchups(CassiopeiaLazyList):
    _data_types = {ChampionGGMatchupListData}

    def __init__(self, *, id: int, role: Union[Role, str], patch: Union[Patch, str], elo: Set[str] = None, region: [Region, str] = None):
        if not isinstance(role, Role):
            role = Role(role)
        if region is not None and not isinstance(region, Region):
            region = Region(region)
        kwargs = {}
        CassiopeiaObject.__init__(self, **kwargs)
        SearchableLazyList.__init__(self, iter([]))

        if elo is None:
            elo = "PLATINUM_DIAMOND_MASTER_CHALLENGER"
        elif isinstance(elo, str):
            if "_" in elo:
                elo = elo.split("_")
            elif "," in elo:
                elo = elo.split(",")
        self._patch = patch
        self._role = role
        self._elo = elo
        self._id = id
        self._region = region

    @classmethod
    def __get_query_from_kwargs__(cls, *, id: int, role: Union[Role, str], patch: Union[Patch, str], elo: Set[str] = None, region: [Region, str] = None) -> dict:
        if isinstance(role, Role):
            role = role.value
        if isinstance(patch, Patch):
            patch = patch.name
        if isinstance(elo, list):
            elo = "_".join(elo)
        if isinstance(region, Region):
            region = region.value
        query = {"role": role, "id": id, "patch": patch, "elo": elo}
        return query


class ChampionGGStats(CassiopeiaGhost):
    _data_types = {ChampionGGStatsData}

    def __init__(self, *, id: int, role: Union[Role, str], patch: Union[Patch, str], elo: Set[str] = None, region: Union[Region, str] = None):
        if not isinstance(role, Role):
            role = Role(role)
        if region is None:
            region = configuration.settings.default_region
        if region is not None and not isinstance(region, Region):
            region = Region(region)
        if elo is None:
            elo = "PLATINUM_DIAMOND_MASTER_CHALLENGER"
        elif isinstance(elo, str):
            if "_" in elo:
                elo = elo.split("_")
            elif "," in elo:
                elo = elo.split(",")
        kwargs = {"id": id}
        super().__init__(**kwargs)
        self._region = region
        self._patch = patch
        self._role = role
        self._elo = elo

    def __get_query__(self):
        return {"id": self.id, "patch": self.patch.name, "elo": "_".join(self.elo), "role": self.role.value}

    @property
    def region(self) -> Region:
        return self._region

    @property
    def elo(self) -> Set[str]:
        return self._elo

    @property
    def patch(self) -> Patch:
        return self._patch

    @property
    def role(self) -> Role:
        return self._role

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def id(self) -> int:
        return self._data[ChampionGGStatsData].id

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def win_rate(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].winRate

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def play_rate(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].playRate

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def play_rate_by_role(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].playRateByRole

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def ban_rate(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].banRate

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def games_played(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].gamesPlayed

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def damage_composition(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].damageComposition

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def kills(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].kills

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def total_damage_taken(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].totalDamageTaken

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def wards_killed(self) -> SearchableDictionary:
        print(self._data[ChampionGGStatsData].to_dict().keys())
        return self._data[ChampionGGStatsData].wardsKilled

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def neutral_minions_killed_in_team_jungle(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].neutralMinionsKilledInTeamJungle

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def assists(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].assists

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def performance_score(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].performanceScore

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def neutral_minions_killed_in_enemy_jungle(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].neutralMinionsKilledInEnemyJungle

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def gold_earned(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].goldEarned

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def deaths(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].deaths

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def minions_killed(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].minionsKilled

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def total_healed(self) -> SearchableDictionary:
        return self._data[ChampionGGStatsData].totalHealed

    @CassiopeiaGhost.property(ChampionGGStatsData)
    @ghost_load_on(AttributeError)
    def championgg_metadata(self) -> dict:
        return {
            "elo": [Tier(tier) for tier in self._data[ChampionGGStatsData].elo],
            "patch": self.patch
        }

    @lazy_property
    def matchups(self) -> list:
        return ChampionGGMatchups(id=self.id, region=self.region, role=self.role, patch=self.patch, elo=self.elo)


class ChampionGGChampion(object):
    _data_types = {ChampionGGChampionData}

    def __init__(self, *, id: int, patch: Patch, elo: Set[str] = None, region: Union[Region, str] = None):
        self._id = id
        if region is None:
            region = configuration.settings.default_region
        if region is not None and not isinstance(region, Region):
            region = Region(region)
        if elo is None:
            elo = "PLATINUM_DIAMOND_MASTER_CHALLENGER"
        self._region = region
        self._elo = elo
        if isinstance(patch, str):
            patch = Patch.from_str(patch, region=region)
        self._patch = patch
        self.roles = {}

    def __get_query__(self):
        return {"id": self.id, "patch": self.patch.name, "elo": "_".join(self.elo)}

    @lazy_property
    def region(self) -> Region:
        return self._region

    @property
    def elo(self) -> Set[str]:
        return self._elo

    @property
    def patch(self) -> Patch:
        return self._patch

    @property
    def id(self) -> int:
        return self._id

    def __getitem__(self, role):
        if isinstance(role, Role):
            role = role.value
        if role not in self.roles:
            self.roles[role] = ChampionGGStats(id=self.id, patch=self.patch, elo=self.elo, region=self.region, role=role).load(load_groups={ChampionGGStatsData})
        return self.roles[role]

    def load(self):
        for role in Role:
            try:
                self[role]
            except NotFoundError:
                continue
