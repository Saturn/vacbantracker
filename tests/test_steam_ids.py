from app.steam.id import (is_valid_steamid,
                          is_steamid,
                          is_steamid64,
                          is_steamid3,
                          steamid_to_steamid64,
                          steamid64_to_steamid,
                          steamid64_to_steamid3,
                          steamid3_to_steamid,
                          SteamID)


steamids_a = ['76561197960359452', 'STEAM_0:0:46862', '[U:1:93724]']
steamids_b = ['76561198066693739', 'STEAM_0:1:53214005', '[U:1:106428011]']


def test_valid_steamid():
    for steamid in steamids_a + steamids_b:
        assert is_valid_steamid(steamid)


def test_is_steamid():
    assert is_steamid(steamids_a[1])
    assert is_steamid(steamids_b[1])


def test_is_steamid64():
    assert is_steamid64(steamids_a[0])
    assert is_steamid64(steamids_b[0])


def test_is_steamid3():
    assert is_steamid3(steamids_a[2])
    assert is_steamid3(steamids_b[2])


def test_convert_steamid_to_steamid64():
    steamid_a, steamid_b = steamids_a[1], steamids_b[1]
    assert steamid_to_steamid64(steamid_a) == steamids_a[0]
    assert steamid_to_steamid64(steamid_b) == steamids_b[0]


def test_convert_steamid64_to_steamid():
    steamid64_a, steamid64_b = steamids_a[0], steamids_b[0]
    assert steamid64_to_steamid(steamid64_a) == steamids_a[1]
    assert steamid64_to_steamid(steamid64_b) == steamids_b[1]


def test_convert_steamid64_to_steamid3():
    steamid64_a, steamid64_b = steamids_a[0], steamids_b[0]
    assert steamid64_to_steamid3(steamid64_a) == steamids_a[2]
    assert steamid64_to_steamid3(steamid64_b) == steamids_b[2]


def test_convert_steamid3_to_steamid():
    steamid3_a, steamid3_b = steamids_a[2], steamids_b[2]
    assert steamid3_to_steamid(steamid3_a) == steamids_a[1]
    assert steamid3_to_steamid(steamid3_b) == steamids_b[1]


def test_steamid_from_steamid():
    steamid_a, steamid_b = steamids_a[1], steamids_b[1]
    a = SteamID(steamid_a)
    b = SteamID(steamid_b)
    assert a.steamid == steamids_a[1]
    assert a.steamid64 == steamids_a[0]
    assert a.steamid3 == steamids_a[2]
    assert b.steamid == steamids_b[1]
    assert b.steamid64 == steamids_b[0]
    assert b.steamid3 == steamids_b[2]


def test_steamid_from_steamid64():
    steamid_a, steamid_b = steamids_a[0], steamids_b[0]
    a = SteamID(steamid_a)
    b = SteamID(steamid_b)
    assert a.steamid == steamids_a[1]
    assert a.steamid64 == steamids_a[0]
    assert a.steamid3 == steamids_a[2]
    assert b.steamid == steamids_b[1]
    assert b.steamid64 == steamids_b[0]
    assert b.steamid3 == steamids_b[2]


def test_steamid_from_steamid3():
    steamid_a, steamid_b = steamids_a[2], steamids_b[2]
    a = SteamID(steamid_a)
    b = SteamID(steamid_b)
    assert a.steamid == steamids_a[1]
    assert a.steamid64 == steamids_a[0]
    assert a.steamid3 == steamids_a[2]
    assert b.steamid == steamids_b[1]
    assert b.steamid64 == steamids_b[0]
    assert b.steamid3 == steamids_b[2]
