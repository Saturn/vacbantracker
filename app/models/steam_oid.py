from app.extensions import db


class SteamOID(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))

    profile = db.relationship('Profile', uselist=False)

    @property
    def personaname(self):
        return self.profile.personaname

    @property
    def steamid(self):
        return self.profile.steamid

    def __repr__(self):
        return '<SteamOID {} steamid: {}>'.format(self.personaname, self.steamid)
