from app import db
from app.models.user import User
from app.models.profile import Profile


# for use with the test data
STEAMID = '76561198066693739'
STEAMIDS = ['76561197960359452',
            '76561198034202275',
            '76561197988627193',
            '76561197987713664',
            '76561197982036918']


def test_create_steam_user(setup_app_and_db, mock_steam_single):
    with mock_steam_single:
        u = User.get_or_create_steam_user(STEAMID)
        assert u.steam_oid is not None
        assert u.steam_oid.profile.steamid == STEAMID


def test_get_steam_user(setup_app_and_db, mock_steam_single):
    with mock_steam_single:
        u = User.get_or_create_steam_user(STEAMID)
        assert User.get_or_create_steam_user(STEAMID) is u


def test_is_steam_user(setup_app_and_db, mock_steam_single):
    with mock_steam_single:
        u = User.get_or_create_steam_user(STEAMID)
        assert u.steam_user


def test_is_not_steam_user(setup_app_and_db):
    u = User(email='bob@example.com')
    assert not u.steam_user


def test_user_track_profile(setup_app_and_db, mock_steam_single):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([STEAMID])
        is_tracked = u.track_profile(STEAMID)
    assert is_tracked


def test_user_untrack_profile(setup_app_and_db, mock_steam_single):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([STEAMID])
        u.track_profile(STEAMID)
        is_untracked = u.untrack_profile(STEAMID)
    assert is_untracked


def test_user_untrack_profile_not_tracking(setup_app_and_db, mock_steam_single):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([STEAMID])
        is_untracked = u.untrack_profile(STEAMID)
    assert not is_untracked


def test_steam_user_tracking_themselves(setup_app_and_db, mock_steam_single):
    with mock_steam_single:
        u = User.get_or_create_steam_user(STEAMID)
        assert not u.track_profile(STEAMID)


def test_user_already_tracking_profile(setup_app_and_db, mock_steam_single):
    u = User()
    db.session.add(u)
    db.session.commit()
    with mock_steam_single:
        Profile.get_profiles([STEAMID])
        u.track_profile(STEAMID)
        is_tracked = u.track_profile(STEAMID)
    assert not is_tracked
