from merakicommons.cache import lazy_property

import cassiopeia
from cassiopeia.core.common import get_latest_version
from cassiopeia.core.staticdata.champion import Champion
from cassiopeia.core.patch import Patch
from .core import ChampionGGChampion
from .datastores import ChampionGG
from .transformers import ChampionGGTransformer
from .data import Role

__transformers__ = [ChampionGGTransformer()]

# Monkey patch in the Champion.championgg object

def championgg(self) -> ChampionGGChampion:
    """The champion.gg data for this champion."""
    latest_version = get_latest_version(self.region, endpoint="champion")
    if self.version != latest_version:
        raise ValueError("Can only get champion.gg data for champions on the most recent version.")
    patch_name = ".".join(self.version.split(".")[:-1])
    try:
        patch = Patch.from_str(patch_name, region=self.region)
    except ValueError:
        patch = Patch(region=self.region, season=None, name=patch_name, start=None, end=None)
    return ChampionGGChampion(id=self.id, patch=patch, region=self.region)

championgg = lazy_property(championgg)

Champion.championgg = championgg

# Monkey patch in the Role as well
cassiopeia.RoleGG = Role
