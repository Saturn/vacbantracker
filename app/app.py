import os

import click

from app import create_app, db, login_manager

from app.models.user import User
from app.models.profile import Profile
from app.models.tracking import Tracking
from app.models.steam_oid import SteamOID

from app.steam.api import (get_summaries,
                           get_bans,
                           get_summaries_and_bans)


def to_dict(model):
    cols = model.__table__.columns.keys()
    return {x: getattr(model, x) for x in cols}


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


app = create_app('default')

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_PATH = ROOT_PATH + '/../tests/'


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Profile=Profile,
                Tracking=Tracking,
                SteamOID=SteamOID,
                get_summaries=get_summaries,
                get_bans=get_bans,
                get_summaries_and_bans=get_summaries_and_bans,
                to_dict=to_dict,
                u=User.query.first())


@app.cli.command('initdb', help='Recreate db.')
def initdb():
    if app.config['ENV'] == 'development':
        db.drop_all()
        db.create_all()
        u = User(email='patrick@example.org',
                 password='password1')
        db.session.add(u)
        db.session.commit()


@app.cli.command('test', help='Run tests')
@click.option('--coverage', is_flag=True,
              help='Run tests with coverage.')
def run_tests(coverage):
    import pytest
    import subprocess
    if coverage:
        subprocess.call(['pytest',
                         TEST_PATH,
                         '--doctest-modules',
                         '-v',
                         '--cov',
                         'app'])
    else:
        pytest.main(['-v', TEST_PATH])
