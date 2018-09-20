from app import create_app, db

from app.models.user import User
from app.models.profile import Profile
from app.models.tracking import Tracking
from app.steam.api import get_summaries, get_bans, get_summaries_and_bans


app = create_app('default')


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db,
                User=User,
                Profile=Profile,
                Tracking=Tracking,
                get_summaries=get_summaries,
                get_bans=get_bans,
                get_summaries_and_bans=get_summaries_and_bans)


@app.cli.command('initdb', help='Recreate db')
def initdb():
    db.drop_all()
    db.create_all()
