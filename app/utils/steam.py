import re


BASE_STEAM_ID = 76561197960265728

steamid_regexes = {
    'vanity': re.compile('steamcommunity.com\/id\/(\w*)'),
    'steamid': re.compile('STEAM_[0|1]:[0|1]:\d+'),
    'steamid64': re.compile('7656119+\d{10}'),
    'steamid3': re.compile('\[U:1:\d+\]')
    }


def is_valid_steamid(steamid):
    """
    Checks if steamid is valid
    """
    return any(re.match(x, steamid) for x in steamid_regexes.values())


def is_steamid(steamid):
    return re.match(steamid_regexes['steamid'], steamid) is not None


def is_steamid64(steamid):
    return re.match(steamid_regexes['steamid64'], steamid) is not None


def is_steamid3(steamid):
    return re.match(steamid_regexes['steamid3'], steamid) is not None


def steamid64_to_steamid(steamid):
    """
    convert steamid in form [76561197960265728] to [STEAM_0:X:Y]
    """
    new_steamid = int(steamid) - BASE_STEAM_ID
    return 'STEAM_0:{}:{}'.format(new_steamid % 2, steamid // 2)


def steamid_to_steamid64(steamid):
    """
    convert steamid in form [STEAM_0:X:Y] to [76561197960265728]
    """
    # [STEAM_0:X:Y]
    x_part, y_part = steamid.split(':')[1:]
    steamid64 = BASE_STEAM_ID + int(y_part) * 2
    if x_part == '1':
        steamid64 += 1
    return steamid64


def steamid64_to_steamid3(steamid):
    """
    convert steamid in form [76561197960265728] to [[U:1:A]]
    """
    new_steamid = int(steamid) - BASE_STEAM_ID
    return "[U:1:{}]".format(new_steamid)


def steamid3_to_steamid(steamid):
    """
    convert steamid in form [[U:1:A]] to [STEAM_0:X:Y]
    """
    steamid = steamid[1:-1]  # remove outer brackets
    A_part = steamid.split(':')[2]
    y_part, x_part = divmod(int(A_part), 2)
    return 'STEAM_0:{}:{}'.format(x_part, y_part)


class SteamProfile:
    def __init__(self, steamid):
        """
        steamid can be in form [STEAM_0:X:Y], [76561197960265728] or [[U:1:A]]
        """
        _steamid, _steamid64, _steamid3 = None, None, None

        if is_steamid(steamid):
            _steamid = steamid
            _steamid64 = steamid_to_steamid64(steamid)
            _steamid3 = steamid64_to_steamid3(_steamid64)
        elif is_steamid64(steamid):
            _steamid = steamid64_to_steamid(steamid)
            _steamid64 = steamid
            _steamid3 = steamid64_to_steamid3(_steamid64)
        elif is_steamid3(steamid):
            _steamid = steamid3_to_steamid
            _steamid64 = steamid_to_steamid64(_steamid)
            _steamid3 = steamid

        self.steamid = _steamid
        self.steamid64 = _steamid64
        self.steamid3 = _steamid3

    def __repr__(self):
        return '<SteamProfile [{}]>'.format(self.steamid)
