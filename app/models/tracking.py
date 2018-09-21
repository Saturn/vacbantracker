from datetime import datetime

from app.extensions import db


class Tracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    note = db.Column(db.String(1024))
    timetracked = db.Column(db.DateTime, default=datetime.utcnow())

    # x_col's are set when user tracks a steam profile
    # They represent the state at that time.
    x_personaname = db.Column(db.String(255))
    x_community_banned = db.Column(db.Boolean)
    x_days_since_last_ban = db.Column(db.Integer)
    x_economy_ban = db.Column(db.String(255))
    x_num_game_bans = db.Column(db.Integer)
    x_num_vac_bans = db.Column(db.Integer)
    x_vac_banned = db.Column(db.Boolean)

    profile = db.relationship('Profile', uselist=False)

    def __repr__(self):
        return '<Tracking steamid={} user={}>'.format(self.profile.steamid,
                                                      self.user.id)
