## champion.gg plugin

This plugin provides champion and matchup information from champion.gg's API (api.champion.gg).

The data is accessible through the `.championgg` attribute on Cassiopeia's `Champion` objects. For example:

```
from cassiopeia import Champion, Role
lux = Champion(name="Lux", region="NA")

# Get data by role
lux.championgg[Role.middle].win_rate  # 0.516962691476365
lux.championgg[Role.support].win_rate  # 0.49831291067305983

# Get matchup data for Lux mid
for matchup in lux.championgg[Role.middle].matchups:
    if matchup.nmatches > 100:
        print(f"{matchup.enemy.champion.name}: {round(matchup.winrate*100)}%   ({matchup.nmatches} matches analyzed)")
# Ekko: 51%   (347 matches analyzed)
# Zed: 53%   (560 matches analyzed)
# Vel'Koz: 50%   (212 matches analyzed)
# Yasuo: 50%   (473 matches analyzed)
```


## Setup

See the [Cassiopeia documentation](http://cassiopeia.readthedocs.org/en/latest).
