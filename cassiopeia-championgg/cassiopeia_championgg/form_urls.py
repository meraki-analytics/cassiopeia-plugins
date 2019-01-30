from typing import Optional

ROLES = ['TOP', 'JUNGLE', 'MIDDLE', 'SYNERGY', 'ADCSUPPORT', 'DUO_CARRY']
ELOS = ['BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'PLATINUM_DIAMOND_MASTER_CHALLENGER']


def get_site_information_url(api_key: str, elo: str = 'PLATINUM_DIAMOND_MASTER_CHALLENGER'):
    elo = elo.upper()
    if elo not in ELOS:
        raise ValueError(f"`elo` must be one of: {', '.join(ELOS)}. Got {elo}.")
    url = f"https://api.champion.gg/v2/general"
    params = {
        'elo': elo,
        'api_key': api_key
    }
    return url, params


def get_overall_champion_url(api_key: str, elo: str = 'PLATINUM_DIAMOND_MASTER_CHALLENGER'):
    elo = elo.upper()
    if elo not in ELOS:
        raise ValueError(f"`elo` must be one of: {', '.join(ELOS)}. Got {elo}.")
    url = f"https://api.champion.gg/v2/overall"
    params = {
        'elo': elo,
        'api_key': api_key
    }
    return url, params


def get_champion_url(api_key: str,
                     elo: str = 'PLATINUM_DIAMOND_MASTER_CHALLENGER',
                     win_rate: bool = True,  # float
                     play_rate: bool = True,  # float
                     percent_role_played: bool = True,  # float
                     ban_rate: bool = True,  # float
                     kda: bool = True,  # float
                     gold_earned: bool = True,  # float
                     minions_killed: bool = True,  # int
                     damage: bool = True,  # dict
                     total_healed: bool = True,  # float
                     items_runes_skills: bool = True,  # dict
                     normalize_by_role: bool = False,
                     wins_by_matches_played: bool = False,  # dict
                     games_played: bool = False,  # int
                     wards_placed: bool = False,  # float
                     positions: bool = False,  # dict
                     average_number_of_games: bool = False,  # float
                     overall_performance_score: bool = False,  # float
                     killing_sprees: bool = False,  # float
                     max_mins: bool = False,  # dict
                     matchups: bool = False,  # dict
                     #runes: bool = True, skills: bool = True, first_items: bool = True, final_items: bool = True, trinkets:  bool = True, summoners: bool = False, grouped_wins: bool = False,
                     champion: Optional[int] = None,
                     ):
    elo = elo.upper()
    if elo not in ELOS:
        raise ValueError(f"`elo` must be one of: {', '.join(ELOS)}. Got {elo}.")
    num_results = 500
    skip = 0
    sort = 'winRate-desc'

    champion_data = {'role'}
    if win_rate: champion_data.add('winRate')
    if play_rate: champion_data.add('playRate')
    if percent_role_played: champion_data.add('percentRolePlayed')
    if ban_rate: champion_data.add('banRate')
    if kda: champion_data.add('kda')
    if damage: champion_data.add('damage')
    if minions_killed: champion_data.add('minions')
    if wins_by_matches_played: champion_data.add('wins')
    if games_played: champion_data.add('gamesPlayed')
    if wards_placed: champion_data.add('wards')
    if positions: champion_data.add('positions')
    if normalize_by_role: champion_data.add('normalized')
    if average_number_of_games: champion_data.add('averageGames')
    if overall_performance_score: champion_data.add('overallPerformanceScore')
    if killing_sprees: champion_data.add('killingSprees')
    if items_runes_skills: champion_data.add('hashes')
    if max_mins: champion_data.add('maxMins')
    if matchups: champion_data.add('matchups')
    if gold_earned: champion_data.add('goldEarned')
    if total_healed: champion_data.add('totalHeal')
    #if runes: champion_data.add('rnes')
    #if skills: champion_data.add('skills')
    #if first_items: champion_data.add('firstitems')
    #if final_items: champion_data.add('finalitems')
    #if trinkets: champion_data.add('trinkets')
    #if summoners: champion_data.add('summoners')
    #if grouped_wins: champion_data.add('groupedWins')

    if champion is None:
        url = f"https://api.champion.gg/v2/champions"
    else:
        url = f"https://api.champion.gg/v2/champions/{champion}"
    params = {
        'elo': elo,
        'champData': ','.join(champion_data),
        'limit': num_results,
        'skip': skip,
        'sort': sort,
        'api_key': api_key,
    }
    return url, params


def get_champion_matchup_url(api_key: str, id: int, role: Optional[str] = None, elo: str = 'PLATINUM_DIAMOND_MASTER_CHALLENGER', num_results: int = 99999):
    elo = elo.upper()
    if elo not in ELOS:
        raise ValueError(f"`elo` must be one of: {', '.join(ELOS)}. Got {elo}.")
    skip = 0
    params = {
        'elo': elo,
        'limit': num_results,
        'skip': skip,
        'api_key': api_key
    }
    if role is None:
        url = f"https://api.champion.gg/v2/champions/{id}/matchups"
    else:
        role = role.upper()
        if role not in ['TOP', 'JUNGLE', 'MIDDLE', 'SYNERGY', 'ADCSUPPORT', 'DUO_CARRY']:
            raise ValueError("`role` must be one of: TOP, JUNGLE, MIDDLE, SYNERGY, ADCSUPPORT, DUO_CARRY")
        url = f"https://api.champion.gg/v2/champions/{id}/{role}/matchups"
    return url, params
