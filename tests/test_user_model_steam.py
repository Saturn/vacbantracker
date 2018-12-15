from app import db
from app.models.user import User
from app.models.profile import Profile


def test_create_steam_user(setup_app_and_db, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_oid is not None
        assert u.steam_oid.profile.steamid == steamid


def test_get_steam_user(setup_app_and_db, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert User.get_or_create_steam_user(steamid) is u


def test_is_steam_user(setup_app_and_db, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_user


def test_is_not_steam_user(setup_app_and_db):
    u = User(email='bob@example.com')
    assert not u.steam_user


def test_user_track_profile(setup_app_and_db, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        is_tracked = u.track_profile(steamid)
    assert is_tracked


def test_user_untrack_profile(setup_app_and_db, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_untracked = u.untrack_profile(steamid)
    assert is_untracked


def test_user_untrack_profile_not_tracking(setup_app_and_db, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        is_untracked = u.untrack_profile(steamid)
    assert not is_untracked


def test_steam_user_tracking_themselves(setup_app_and_db, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert not u.track_profile(steamid)


def test_user_already_tracking_profile(setup_app_and_db, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_tracked = u.track_profile(steamid)
    assert not is_tracked
