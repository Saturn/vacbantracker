from app.extensions import db
from app.utils import unix_ts_to_dt


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.String(255), nullable=False)
    communityvisibilitystate = db.Column(db.Integer, nullable=False)
    profilestate = db.Column(db.Integer, nullable=False)
    personaname = db.Column(db.String(255))
    lastlogoff = db.Column(db.DateTime, default=lambda x: unix_ts_to_dt(x))
    profileurl = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    avatarmedium = db.Column(db.String(255))
    avatarfull = db.Column(db.String(255))
    personastate = db.Column(db.Integer, nullable=False)

    # optional
    commentpermission = db.Column(db.Integer)
    realname = db.Column(db.String(255))
    primaryclanid = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime, default=lambda x: unix_ts_to_dt(x))
    loccountrycode = db.Column(db.String(255))
    locstatecode = db.Column(db.String(255))
    loccityid = db.Column(db.Integer)
    gameid = db.Column(db.String(255))
    gameextrainfo = db.Column(db.String(255))
    gameserverip = db.Column(db.String(255))

    def __init__(self, **kwargs):
        if 'personastateflags' in kwargs:
            del(kwargs['personastateflags'])
        super(Profile, self).__init__(**kwargs)

    def __repr__(self):
        return '<Profile steamid={}>'.format(self.steamid)
