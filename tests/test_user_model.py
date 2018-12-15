import time
from unittest.mock import patch

import pytest

from app import db
from app.models.user import User
from app.models.profile import Profile


def test_user_create(setup_app_and_db):
    u = User()
    db.session.add(u)
    db.session.commit()


def test_password_set(setup_app_and_db):
    u = User(password='testing1')
    assert u._password is not None


def test_password_get(setup_app_and_db):
    u = User(password='testing1')
    assert u.password == u._password


def test_verify_correct_password(setup_app_and_db):
    u = User(password='testing1')
    assert u.verify_pw('testing1')


def test_verify_incorrect_password(setup_app_and_db):
    u = User(password='testing1')
    assert not u.verify_pw('testing2')


def test_password_salt(setup_app_and_db):
    u1 = User(password='testing1')
    u2 = User(password='testing1')
    assert u1.password != u2.password


def test_password_change(setup_app_and_db):
    u = User(password='testing1')
    u.password = 'testing13'
    assert not u.verify_pw('testing1')
    assert u.verify_pw('testing13')


def test_valid_password_change_token(setup_app_and_db):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    token = u.generate_forgot_password_token()
    assert u.validate_forgot_password_token(token)


def test_invalid_password_change_token(setup_app_and_db):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    assert u.validate_forgot_password_token('FaKeToKEn') is None


def test_expired_password_change_token(setup_app_and_db):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    token = u.generate_forgot_password_token()
    current_time = time.time()
    with patch('time.time') as p:
        p.return_value = int(current_time + 10000)
        valid_password_change = u.validate_forgot_password_token(token)
        assert not valid_password_change


def test_email_verification_token(setup_app_and_db):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    assert u.validate_email(token) == 'verified'


def test_expired_email_change_token(setup_app_and_db):
    u = User(password='testing1',
             email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    current_time = time.time()
    with patch('time.time') as p:
        p.return_value = int(current_time + 24*60*60 + 1)
        validate_email = u.validate_email(token)
        assert not validate_email == 'verified'
        assert validate_email == 'signature_expired'


def test_invalid_signature_email_token(setup_app_and_db):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    assert u.validate_email('ODJIAWIOEDJASWOD') == 'bad_signature'


def test_invalid_user_email_token(setup_app_and_db):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    db.session.delete(u)
    db.session.commit()
    assert User.validate_email(token) == 'unverified'


def test_email_verification_without_email(setup_app_and_db):
    u = User(email=None)
    db.session.add(u)
    db.session.commit()
    with pytest.raises(ValueError):
        u.generate_email_verification_token()


def test_change_email(setup_app_and_db):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    new_email = 'bobnew@example.com'
    u.change_email(new_email)
    assert u.email == new_email


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
