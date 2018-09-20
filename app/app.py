from app import create_app, db, login_manager

from app.models.user import User
from app.models.profile import Profile
from app.models.tracking import Tracking
from app.models.steam_oid import SteamOID

from app.steam.api import get_summaries, get_bans, get_summaries_and_bans


app = create_app('default')


@login_manager.user_loader
def user_loader(id):
    return User.query.get(int(id))


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
                get_summaries_and_bans=get_summaries_and_bans)


@app.cli.command('initdb', help='Recreate db')
def initdb():
    db.drop_all()
    db.create_all()
