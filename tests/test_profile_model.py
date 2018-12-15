from app.models.profile import Profile


def test_get_profile(setup, steamid):
    Profile.get_profile(steamid)
    profile = Profile.query.first()
    assert profile.steamid == steamid


def test_get_profiles(setup, steamids):
    Profile.get_profiles(steamids)
    profiles = Profile.query.all()
    for profile in profiles:
        assert profile.steamid in steamids
