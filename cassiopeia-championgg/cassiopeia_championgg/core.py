from typing import Set, Union

from merakicommons.ghost import ghost_load_on
from merakicommons.container import SearchableDictionary
from merakicommons.cache import lazy_property

from datapipelines import NotFoundError

from cassiopeia import configuration
from cassiopeia.data import Region, Role, Tier
from cassiopeia.core.common import CoreData, CassiopeiaGhost, CoreDataList
from cassiopeia.core.patch import Patch

from .dto import ChampionGGDto, ChampionGGListDto


class ChampionGGListData(CoreDataList):
    _dto_type = ChampionGGListDto
    _renamed = {"included_data": "includedData"}

    @property
    def region(self) -> str:
        return self._dto["region"]


class ChampionGGData(CoreData):
    _dto_type = ChampionGGDto
    _renamed = {"championId": "id", "overallPerformanceScore": "performanceScore", "percentRolePlayed": "playRateByRole", "totalHeal": "totalHealed", "neutralMinionsKilledTeamJungle": "neutralMinionsKilledInTeamJungle", "neutralMinionsKilledEnemyJungle": "neutralMinionsKilledInEnemyJungle", "included_data": "includedData"}

    def __call__(self, **kwargs):
        if "elo" in kwargs:
            self.elo = kwargs.pop("elo").split(",")
        if "champData" in kwargs:
            self.includedData = kwargs.pop("champData").split(",")
        if "included_data" in kwargs:
            self.includedData = kwargs.pop("included_data").split(",")
        super().__call__(**kwargs)
        return self


class ChampionGGStats(CassiopeiaGhost):
    _data_types = {ChampionGGData}

    def __init__(self, *, id: int, patch: Patch, included_data: Set[str] = None, elo: Set[str] = None, region: Union[Region, str] = None):
        if region is None:
            region = configuration.settings.default_region
        if region is not None and not isinstance(region, Region):
            region = Region(region)
        if included_data is None:
            # I manually chose a selection of data to return by default; I chose this data because it's relatively small and provides some additional useful information.
            included_data = "kda,damage,minions,wards,overallPerformanceScore,goldEarned"
        if elo is None:
            elo = "PLATINUM_DIAMOND_MASTER_CHALLENGER"
        kwargs = {"region": region, "id": id, "patch": patch.name, "elo": elo, "included_data": included_data}
        super().__init__(**kwargs)
        self._patch = patch

    def __get_query__(self):
        return {"id": self.id, "patch": self.patch.name, "includedData": ",".join(self.included_data), "elo": "_".join(self.elo)}

    @lazy_property
    def region(self) -> Region:
        return Region(self._data[ChampionGGData].region)

    @property
    def included_data(self) -> Set[str]:
        return self._data[ChampionGGData].includedData

    @property
    def elo(self) -> Set[str]:
        return self._data[ChampionGGData].elo

    @property
    def patch(self) -> Patch:
        return self._patch

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def id(self) -> int:
        return self._data[ChampionGGData].id

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def win_rate(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].winRate.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def play_rate(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].playRate.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def play_rate_by_role(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].playRateByRole.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def ban_rate(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].banRate.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def games_played(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].gamesPlayed.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def damage_composition(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].damageComposition.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def kills(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].kills.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def total_damage_taken(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].totalDamageTaken.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def wards_killed(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].wardsKilled.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def neutral_minions_killed_in_team_jungle(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].neutralMinionsKilledInTeamJungle.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def assists(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].assists.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def performance_score(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].performanceScore.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def neutral_minions_killed_in_enemy_jungle(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].neutralMinionsKilledInEnemyJungle.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def gold_earned(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].goldEarned.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def deaths(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].deaths.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def minions_killed(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].minionsKilled.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def total_healed(self) -> SearchableDictionary:
        return SearchableDictionary({Role(role): value for role, value in self._data[ChampionGGData].totalHealed.items()})

    @CassiopeiaGhost.property(ChampionGGData)
    @ghost_load_on(AttributeError)
    def championgg_metadata(self) -> dict:
        return {
            "elo": [Tier(tier) for tier in self._data[ChampionGGData].elo],
            "patch": self.patch
        }
