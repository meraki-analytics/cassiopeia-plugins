from merakicommons.cache import lazy_property

from cassiopeia.core.common import get_latest_version
from cassiopeia.core.staticdata.champion import Champion
from cassiopeia.core.patch import Patch
from .core import ChampionGGStats
from .datastores import ChampionGG
from .transformers import ChampionGGTransformer

__transformers__ = [ChampionGGTransformer()]

# Monkey patch in the Champion.championgg object

def championgg(self) -> ChampionGGStats:
    """The champion.gg data for this champion."""
    latest_version = get_latest_version(self.region, endpoint="champion")
    if self.version != latest_version:
        raise ValueError("Can only get champion.gg data for champions on the most recent version.")
    return ChampionGGStats(id=self.id, patch=Patch.from_str(".".join(self.version.split(".")[:-1]), region=self.region), region=self.region)

championgg = lazy_property(championgg)

Champion.championgg = championgg
