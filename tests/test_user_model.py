import json
import pytest
import requests_mock


from app.models.user import User
from app import db, create_app


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


def test_get_or_create_steam_user(setup):
    bans = summaries = None
    with open('tests/data/bans.json', 'r') as f:
        bans = json.loads(f.read())
    with open('tests/data/summaries.json', 'r') as f:
        summaries = json.loads(f.read())

    mock = requests_mock.mock()
    with mock as m:
        m.get('http://api.steampowered.com/ISteamUser/GetPlayerBans/v1',
              json=bans)
        m.get('http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2',
              json=summaries)

        steamid = '76561198066693739'
        u = User.get_or_create_steam_user(steamid)
        assert u.steam_oid is not None
        assert u.steam_oid.profile.steamid == steamid
