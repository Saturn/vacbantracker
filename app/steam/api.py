import os
from datetime import datetime

from requests import get

from app.utils import convert_pacific_to_utc, get_pacific_tz_year


steam_api_key = os.environ.get('STEAM_API_KEY')

steam_api_url = 'http://api.steampowered.com/'
player_summaries = steam_api_url + 'ISteamUser/GetPlayerSummaries/v2'
player_bans = steam_api_url + 'ISteamUser/GetPlayerBans/v1'
aliases_url = 'https://steamcommunity.com/profiles/{steamid}/ajaxaliases'


def stringify_steamids(list_of_steamids):
    """
    Args:
        list_of_steamids: list of steamids
    Returns:
        Single string with steamids separated by comma
    """
    return ','.join(list(map(str, list_of_steamids)))


def get_summaries(steamids):
    """
    Args:
        steamids: list of steamids
    Returns:
        List of player summaries from Steam API
    """
    steamids = stringify_steamids(steamids)
    summaries = get(player_summaries,
                    params=dict(key=steam_api_key,
                                steamids=steamids))
    if summaries.status_code == 200:
        return summaries.json()['response']['players']


def get_bans(steamids):
    """
    Args:
        steamids: list of steamids
    Returns:
        List of player ban info from Steam API
    """
    steamids = stringify_steamids(steamids)
    bans = get(player_bans,
               params=dict(key=steam_api_key,
                           steamids=steamids))
    if bans.status_code == 200:
        # rename SteamId key to steamid
        data = bans.json()['players']
        for profile in data:
            profile['steamid'] = profile.pop('SteamId')
        return data


def get_summaries_and_bans(steamids):
    """
    Args:
        steamids: list of steamids
    Returns:
        List of player summary and ban info
    """
    summaries = get_summaries(steamids)
    bans = get_bans(steamids)
    merged = []
    for summary in summaries:
        for ban in bans:
            if summary['steamid'] == ban['steamid']:
                merged.append({**summary, **ban})
    return merged
    # faster version?
    # from operator import itemgetter
    # sort_key = operator.itemgetter("steamid")
    # merged = []
    # for summary, ban in zip(sorted(summaries, key=sort_key), sorted(bans, key=sort_key)):
    #     merged.append({**summary, **ban})
    # return merged


def get_aliases(steamid):
    """
    Args:
        steamid: single steamid
    Returns:
        List of aliases from steam profile
    """
    aliases = get(aliases_url.format(steamid=steamid))
    if aliases.status_code == 200:
        aliases = aliases.json()

        # two timechanged formats
        format1 = "%d %b, %Y @ %I:%M%p"
        format2 = "%d %b @ %I:%M%p"
        for alias in aliases:
            try:
                timechanged = datetime.strptime(alias['timechanged'], format1)
            except ValueError:
                timechanged = datetime.strptime(alias['timechanged'], format2)
                timechanged = timechanged.replace(year=get_pacific_tz_year())
            alias['timechanged2'] = convert_pacific_to_utc(timechanged)
        return aliases
