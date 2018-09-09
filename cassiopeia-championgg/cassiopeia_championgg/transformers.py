from typing import Type, TypeVar, List
from collections import defaultdict

from datapipelines import DataTransformer, PipelineContext

from .core import ChampionGGStatsData, ChampionGGStatsListData, ChampionGGMatchupData, ChampionGGMatchupListData, ChampionGGMatchups, ChampionGGMatchup, MultipleChampionGGStatsData, MultipleChampionGGStats
from .dto import ChampionGGStatsDto, ChampionGGStatsListDto, ChampionGGMatchupDto, ChampionGGMatchupListDto, MultipleChampionGGStatsDto

T = TypeVar("T")
F = TypeVar("F")


class ChampionGGTransformer(DataTransformer):
    @DataTransformer.dispatch
    def transform(self, target_type: Type[T], value: F, context: PipelineContext = None) -> T:
        pass

    # Dto to Data

    @transform.register(ChampionGGStatsDto, ChampionGGStatsData)
    def champion_gg_dto_to_data(self, value: ChampionGGStatsDto, context: PipelineContext = None) -> ChampionGGStatsData:
        data = value  # data = deepcopy(value)
        return ChampionGGStatsData(**data)

    @transform.register(MultipleChampionGGStatsDto, MultipleChampionGGStatsData)
    def muliple_champion_gg_dto_to_data(self, value: MultipleChampionGGStatsDto, context: PipelineContext = None) -> MultipleChampionGGStatsData:
        data = value  # data = deepcopy(value)
        return MultipleChampionGGStatsData([ChampionGGTransformer.champion_gg_dto_to_data(None, gg) for gg in data["data"]], id=data["championId"])

    @transform.register(ChampionGGStatsListDto, ChampionGGStatsListData)
    def champion_gg_list_dto_to_data(self, value: ChampionGGStatsListDto, context: PipelineContext = None) -> ChampionGGStatsListData:
        raise NotImplemented  # See functionality in datastores.py
        data = value  # data = deepcopy(value)
        reformatted =  defaultdict(list)
        for item in data["data"]:
            reformatted[item["championId"]].append(item)

        def transform_many_roles_per_champion_to_one_champion(ggs):
            # This function is also in .datastores
            reformatted = defaultdict(dict)
            reformatted["championId"] = ggs[0]["championId"]
            reformatted["elo"] = ggs[0]["elo"]
            reformatted["patch"] = ggs[0]["patch"]
            for data in ggs:
                role = data["role"]
                for field in data.keys():
                    if field in ["championId", "elo", "patch", "role"]:
                        continue
                    reformatted[field][role] = data[field]  # deepcopy(data[field])
            return reformatted

        data = [self.champion_gg_dto_to_data(transform_many_roles_per_champion_to_one_champion(item)) for item in reformatted.values()]
        return ChampionGGStatsListData(data)

    @transform.register(ChampionGGMatchupDto, ChampionGGMatchupData)
    def championgg_matchup_dto_to_data(self, value: ChampionGGMatchupDto, context: PipelineContext = None) -> ChampionGGMatchupData:
        data = value  # data = deepcopy(value)
        return ChampionGGMatchupData(**data)

    @transform.register(ChampionGGMatchupListDto, ChampionGGMatchupListData)
    def championgg_matchup_list_dto_to_data(self, value: ChampionGGMatchupListDto, context: PipelineContext = None) -> ChampionGGMatchupListData:
        data = value
        result = ChampionGGMatchupListData([self.championgg_matchup_dto_to_data(d) for d in data["data"]],
                                           patch=data["patch"],
                                           elo=data["elo"],
                                           id=data["id"],
                                           role=data["role"])
        return result

    # Data to Core

    @transform.register(ChampionGGMatchupData, ChampionGGMatchup)
    def championgg_matchup_data_to_core(self, value: ChampionGGMatchupData, context: PipelineContext = None, correct_champion_id: int = None) -> ChampionGGMatchup:
        data = value  # data = deepcopy(value)
        result = ChampionGGMatchup.from_data(data)
        # TODO This is so hacky...
        result._hack = correct_champion_id
        return result

    @transform.register(ChampionGGMatchupListData, ChampionGGMatchups)
    def championgg_matchups_data_to_core(self, value: ChampionGGMatchupListData, context: PipelineContext = None) -> ChampionGGMatchups:
        data = value  # data = deepcopy(value)
        result = ChampionGGMatchups.from_data(id=data.id, role=data.role, patch=data.patch)
        from collections import Counter
        ids = Counter()
        for d in data:
            ids[d.champ1_id] += 1
            ids[d.champ2_id] += 1
        correct_champion_id = ids.most_common(1)[0][0]
        result._generator = iter([ChampionGGTransformer.championgg_matchup_data_to_core(self, d, correct_champion_id=correct_champion_id) for d in data])
        for matchup in result:
            assert matchup.me.champion.id == correct_champion_id
        return result
