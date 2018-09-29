import os

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

root = os.path.dirname(os.path.realpath(__file__))


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
                to_dict=to_dict)


@app.cli.command('initdb', help='Recreate db')
def initdb():
    db.drop_all()
    db.create_all()


@app.cli.command('test', help='Run tests')
def run_tests():
    import pytest
    pytest.main(['-v', root + '/../tests'])
