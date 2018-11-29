import pytest

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
