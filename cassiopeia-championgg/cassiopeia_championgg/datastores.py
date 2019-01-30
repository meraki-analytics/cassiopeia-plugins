from typing import Type, TypeVar, MutableMapping, Any, Iterable
import os
import copy
import pycurl

from datapipelines import DataSource, PipelineContext, Query, NotFoundError, validate_query
from merakicommons.ratelimits import FixedWindowRateLimiter, MultiRateLimiter

from cassiopeia.datastores.common import HTTPClient, HTTPError
from cassiopeia.datastores.uniquekeys import convert_region_to_platform

from .dto import ChampionGGStatsListDto, ChampionGGStatsDto, ChampionGGMatchupListDto, MultipleChampionGGStatsDto
from .core import ChampionGGStats, MultipleChampionGGStats
from .form_urls import get_champion_url, get_champion_matchup_url

try:
    import ujson as json
except ImportError:
    import json

T = TypeVar("T")
ELOS = ["BRONZE", "SILVER", "GOLD", "PLATINUM", "PLATINUM_DIAMOND_MASTER_CHALLENGER"]
ROLES = ['TOP', 'JUNGLE', 'MIDDLE', 'SYNERGY', 'ADCSUPPORT', 'DUO_CARRY']


class ChampionGG(DataSource):
    def __init__(self, api_key: str, http_client: HTTPClient = None) -> None:
        try:
            api_key = os.environ[api_key]
        except KeyError:
            pass
        self._key = api_key

        if http_client is None:
            self._client = HTTPClient()
        else:
            self._client = http_client

        self._rate_limiter = MultiRateLimiter(
            FixedWindowRateLimiter(600, 3000),
            FixedWindowRateLimiter(10, 50)
        )

        self._cached_data = {}

    @DataSource.dispatch
    def get(self, type: Type[T], query: MutableMapping[str, Any], context: PipelineContext = None) -> T:
        pass

    @DataSource.dispatch
    def get_many(self, type: Type[T], query: MutableMapping[str, Any], context: PipelineContext = None) -> Iterable[T]:
        pass

    #############
    # Champions #
    #############

    _validate_get_gg_champion_list_query = Query. \
        has("patch").as_(str).also. \
        can_have("elo").with_default(lambda *args, **kwargs: "PLATINUM_DIAMOND_MASTER_CHALLENGER", supplies_type=str)

    @get.register(ChampionGGStatsListDto)
    @validate_query(_validate_get_gg_champion_list_query, convert_region_to_platform)
    def get_gg_champion_list(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> ChampionGGStatsListDto:
        if not query["elo"] in ELOS:
            raise ValueError("`elo` must be one of {}. Got \"{}\"".format(ELOS, query["elo"]))

        try:
            return self._cached_data[(self.get_gg_champion_list, (query["patch"], query["elo"]))]
        except KeyError:
            url, params = get_champion_url(api_key=self._key, **{k: v for k, v in query.items() if k != "patch"})
            params = "&".join(["{key}={value}".format(key=key, value=value) for key, value in params.items()])
            try:
                c = pycurl.Curl()
                c.setopt(c.USERAGENT, "Mozilla/5.0")
                data, response_headers = self._client.get(url, params, rate_limiters=[self._rate_limiter], connection=c, encode_parameters=False)
            except HTTPError as error:
                if error.code == 403:
                    raise HTTPError(message="Forbidden", code=error.code)
                raise NotFoundError(str(error)) from error

            for datum in data:
                datum.pop("_id")
            data = {"data": data}
            data["patch"] = query["patch"]
            data["elo"] = query["elo"]
            result = ChampionGGStatsListDto(data)
            self._cached_data[(self.get_gg_champion_list, query["patch"])] = result
            self._cached_data[(self.get_gg_champion_list, (query["patch"], query["elo"]))] = result
            return result

    _validate_get_gg_champion_role_query = Query. \
        has("id").as_(int).also. \
        has("patch").as_(str).also. \
        has("role").as_(str).also. \
        can_have("elo").with_default(lambda *args, **kwargs: "PLATINUM_DIAMOND_MASTER_CHALLENGER", supplies_type=str)

    @get.register(ChampionGGStatsDto)
    @validate_query(_validate_get_gg_champion_role_query, convert_region_to_platform)
    def get_one_champion_from_list(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> ChampionGGStatsDto:
        id = query.pop("id")
        role = query.pop("role")

        items_query = copy.deepcopy(query)
        if "id" in items_query:
            items_query.pop("id")
        if "name" in items_query:
            items_query.pop("name")
        ggs = context[context.Keys.PIPELINE].get(ChampionGGStatsListDto, query=items_query)

        def find_matching_attribute(list_of_dtos, attrs):
            for dto in list_of_dtos:
                if all(dto.get(attrname, None) == attrvalue for attrname, attrvalue in attrs.items()):
                    return dto

        gg = find_matching_attribute(ggs["data"], {"championId": id, "role": role})
        if gg is None:
            raise NotFoundError
        return ChampionGGStatsDto(gg)

    _validate_get_gg_champion_query = Query. \
        has("id").as_(int).also. \
        has("patch").as_(str).also. \
        can_have("elo").with_default(lambda *args, **kwargs: "PLATINUM_DIAMOND_MASTER_CHALLENGER", supplies_type=str)

    @get.register(MultipleChampionGGStatsDto)
    @validate_query(_validate_get_gg_champion_query, convert_region_to_platform)
    def get_one_champion_from_list(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> MultipleChampionGGStatsDto:
        id = query.pop("id")

        items_query = copy.deepcopy(query)
        if "id" in items_query:
            items_query.pop("id")
        if "name" in items_query:
            items_query.pop("name")
        ggs = context[context.Keys.PIPELINE].get(ChampionGGStatsListDto, query=items_query)

        def find_matching_attribute(list_of_dtos, attrs):
            dtos = []
            for dto in list_of_dtos:
                if all(dto.get(attrname, None) == attrvalue for attrname, attrvalue in attrs.items()):
                    dtos.append(dto)
            if dtos:
                return dtos
            else:
                return None

        gg = find_matching_attribute(ggs["data"], {"championId": id})
        if gg is None:
            raise NotFoundError
        return MultipleChampionGGStatsDto({"data": gg, "championId": id})

    ############
    # Matchups #
    ############

    _validate_get_championgg_matchup_list_query = Query. \
        has("id").as_(int).also. \
        has("patch").as_(str).also. \
        has("role").as_(str).also. \
        can_have("elo").with_default(lambda *args, **kwargs: "PLATINUM_DIAMOND_MASTER_CHALLENGER", supplies_type=str)

    @get.register(ChampionGGMatchupListDto)
    @validate_query(_validate_get_championgg_matchup_list_query, convert_region_to_platform)
    def get_championgg_matchups(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> ChampionGGMatchupListDto:
        if not query["elo"] in ELOS:
            raise ValueError("`elo` must be one of {}. Got \"{}\"".format(ELOS, query["elo"]))
        # Need to to some role name transformations here for consistency between Riot's role names and champion.gg's role names
        convert_role = {"TOP": "TOP",
                        "JUNGLE": "JUNGLE",
                        "MIDDLE": "MIDDLE",
                        "DUO_SUPPORT": "ADCSUPPORT",
                        "DUO_CARRY": "DUO_CARRY"
        }
        query["role"] = convert_role[query["role"]]
        if not query["role"] in ROLES:
            raise ValueError("`role` must be one of {}. Got \"{}\"".format(ROLES, query["role"]))

        try:
            data = self._cached_data[(self.get_championgg_matchups, (query["id"], query["patch"], query["elo"], query["role"]))]
        except KeyError:
            url, params = get_champion_matchup_url(api_key=self._key, **{k: v for k, v in query.items() if k != "patch"})
            params = "&".join(["{key}={value}".format(key=key, value=value) for key, value in params.items()])
            try:
                data, response_headers = self._client.get(url, params, rate_limiters=[self._rate_limiter], connection=None, encode_parameters=False)
            except HTTPError as error:
                if error.code == 403:
                    raise HTTPError(message="Forbidden", code=error.code)
                raise NotFoundError(str(error)) from error

            for datum in data:
                datum.pop("_id")
            data = {"data": data}
            data["patch"] = query["patch"]
            data["elo"] = query["elo"]
            for d in data["data"]:
                d["elo"] = query["elo"]
            data["id"] = query["id"]
            data["role"] = query["role"]
            self._cached_data[(self.get_championgg_matchups, (query["id"], query["patch"], query["elo"], query["role"]))] = data
        data = ChampionGGMatchupListDto(data)
        return data

    ##########
    # Ghosts #
    ##########

    @staticmethod
    def create_ghost(cls: Type[T], kwargs) -> T:
        return type.__call__(cls, **kwargs)

    #_validate_get_gg_champion_role_stats_query = Query. \
    #    has("id").as_(int).also. \
    #    has("role").as_(str)

    #@get.register(ChampionGGStats)
    #@validate_query(_validate_get_gg_champion_role_stats_query, convert_region_to_platform)
    #def get_champion(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> ChampionGGStats:
    #    query["region"] = query.pop("platform").region
    #    return ChampionGG.create_ghost(ChampionGGStats, query)

    _validate_get_gg_champion_stats_query = Query. \
        has("id").as_(int)

    @get.register(MultipleChampionGGStats)
    @validate_query(_validate_get_gg_champion_stats_query, convert_region_to_platform)
    def get_champion(self, query: MutableMapping[str, Any], context: PipelineContext = None) -> MultipleChampionGGStats:
        query["region"] = query.pop("platform").region
        return ChampionGG.create_ghost(MultipleChampionGGStats, query)
