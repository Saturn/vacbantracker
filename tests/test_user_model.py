import os

import json
import pytest
import requests_mock


from app.models.user import User
from app.models.profile import Profile
from app import db, create_app

from app.steam.api import PLAYER_BANS_URL, PLAYER_SUMMARIES_URL


TEST_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def setup():
    app = create_app('testing')
    app.app_context = app.app_context()
    app.app_context.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    app.app_context.pop()


@pytest.fixture
def steam_mock():
    ban = summary = None
    data_dir = TEST_PATH + '/data/'
    with open(data_dir + 'ban.json', 'r') as f:
        ban = json.loads(f.read())
    with open(data_dir + 'summary.json', 'r') as f:
        summary = json.loads(f.read())

    mock = requests_mock.mock()
    mock.register_uri('GET',
                      PLAYER_BANS_URL,
                      json=ban)
    mock.register_uri('GET',
                      PLAYER_SUMMARIES_URL,
                      json=summary)
    return mock


def test_user_create(setup):
    u = User()
    db.session.add(u)
    db.session.commit()


def test_password_set(setup):
    u = User(password='testing1')
    assert u._password is not None


def test_password_get(setup):
    u = User(password='testing1')
    assert u.password == u._password


def test_verify_correct_password(setup):
    u = User(password='testing1')
    assert u.verify_pw('testing1')


def test_verify_incorrect_password(setup):
    u = User(password='testing1')
    assert not u.verify_pw('testing2')


def test_password_salt(setup):
    u1 = User(password='testing1')
    u2 = User(password='testing1')
    assert u1.password != u2.password


def test_password_change(setup):
    u = User(password='testing1')
    u.password = 'testing13'
    assert not u.verify_pw('testing1')
    assert u.verify_pw('testing13')


def test_valid_password_change_token(setup):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    token = u.generate_forgot_password_token()
    assert u.validate_forgot_password_token(token)


def test_invalid_password_change_token(setup):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    assert u.validate_forgot_password_token('FaKeToKEn') is None


def test_email_verification_token(setup):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    assert u.validate_email(token) == 'verified'


def test_email_verification_without_email(setup):
    u = User(email=None)
    db.session.add(u)
    db.session.commit()
    with pytest.raises(ValueError):
        u.generate_email_verification_token()


def test_change_email(setup):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    new_email = 'bobnew@example.com'
    u.change_email(new_email)
    assert u.email == new_email


def test_create_steam_user(setup, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_oid is not None
        assert u.steam_oid.profile.steamid == steamid


def test_get_steam_user(setup, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert User.get_or_create_steam_user(steamid) is u


def test_is_steam_user(setup, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_user


def test_is_not_steam_user(setup):
    u = User(email='bob@example.com')
    assert not u.steam_user


def test_user_track_profile(setup, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        is_tracked = u.track_profile(steamid)
    assert is_tracked


def test_user_untrack_profile(setup, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_untracked = u.untrack_profile(steamid)
    assert is_untracked


def test_steam_user_tracking_themselves(setup, steam_mock):
    with steam_mock:
        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert not u.track_profile(steamid)


def test_user_already_tracking_profile(setup, steam_mock):
    u = User()
    db.session.add(u)
    db.session.commit()
    with steam_mock:
        steamid = '76561198066693739'
        Profile.get_profiles([steamid])
        u.track_profile(steamid)
        is_tracked = u.track_profile(steamid)
    assert not is_tracked
