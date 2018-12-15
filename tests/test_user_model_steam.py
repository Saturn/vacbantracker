from app import db
from app.models.user import User
from app.models.profile import Profile


def test_create_steam_user(setup_app_and_db, mock_steam_single, steamid):
    with mock_steam_single:
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_oid is not None
        assert u.steam_oid.profile.steamid == steamid


def test_get_steam_user(setup_app_and_db, mock_steam_single, steamid):
    with mock_steam_single:
        u = User.get_or_create_steam_user(steamid)
        assert User.get_or_create_steam_user(steamid) is u


def test_is_steam_user(setup_app_and_db, mock_steam_single, steamid):
    with mock_steam_single:
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_user


def test_is_not_steam_user(setup_app_and_db):
    u = User(email='bob@example.com')
    assert not u.steam_user


def test_user_track_profile(setup_app_and_db, mock_steam_single, steamid):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([steamid])
        is_tracked = u.track_profile(steamid)
    assert is_tracked


def test_user_untrack_profile(setup_app_and_db, mock_steam_single, steamid):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_untracked = u.untrack_profile(steamid)
    assert is_untracked


def test_user_untrack_profile_not_tracking(setup_app_and_db, mock_steam_single, steamid):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([steamid])
        is_untracked = u.untrack_profile(steamid)
    assert not is_untracked


def test_steam_user_tracking_themselves(setup_app_and_db, mock_steam_single, steamid):
    with mock_steam_single:
        u = User.get_or_create_steam_user(steamid)
        assert not u.track_profile(steamid)


def test_user_already_tracking_profile(setup_app_and_db, mock_steam_single, steamid):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_tracked = u.track_profile(steamid)
    assert not is_tracked


def test_user_get_tracking_all(setup_app_and_db, mock_steam_multiple, steamids):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_multiple:
        Profile.get_profiles(steamids)
    for steamid in steamids:
        u.track_profile(steamid)
    assert len(u.tracking.all()) == len(u.get_tracking(steamids))
    assert len(u.tracking.all()) == len(u.get_tracking())


def test_user_get_tracking_single(setup_app_and_db, mock_steam_multiple, steamids):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_multiple:
        Profile.get_profiles(steamids)
    u.track_profile(steamids[0])
    assert u.tracking.first() == u.get_tracking([steamids[0]])[0]
