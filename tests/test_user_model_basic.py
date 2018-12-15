import pytest

from app import db
from app.models.user import User


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


def test_expired_password_change_token(setup, mock_time):
    u = User(password='testing1')
    db.session.add(u)
    db.session.commit()
    token = u.generate_forgot_password_token()
    with mock_time(seconds=10000):
        valid_password_change = u.validate_forgot_password_token(token)
        assert not valid_password_change


def test_email_verification_token(setup):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    assert u.validate_email(token) == 'verified'


def test_expired_email_change_token(setup, mock_time):
    u = User(password='testing1',
             email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    with mock_time(seconds=24*60*60 + 1):
        validate_email = u.validate_email(token)
        assert not validate_email == 'verified'
        assert validate_email == 'signature_expired'


def test_invalid_signature_email_token(setup):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    assert u.validate_email('ODJIAWIOEDJASWOD') == 'bad_signature'


def test_invalid_user_email_token(setup):
    u = User(email='bob@example.com')
    db.session.add(u)
    db.session.commit()
    token = u.generate_email_verification_token()
    db.session.delete(u)
    db.session.commit()
    assert User.validate_email(token) == 'unverified'


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
