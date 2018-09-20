from datetime import datetime

from flask_login import UserMixin

from app.extensions import db, bcrypt
from app.models.steam_oid import SteamOID


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    _password = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime, default=datetime.utcnow())
    verified = db.Column(db.Boolean, default=False)

    steam_oid = db.relationship('SteamOID', uselist=False)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password, rounds=8)

    def verify_pw(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        output = '<User [Normal] {}>'.format(self.id)
        if self.steam_oid:
            output = '<User [Steam] steamid={}>'.format(self.steam_oid.profile.steamid)
        return output

    @staticmethod
    def get_steam_user(steamid):
        """
        Args:
            steamid Steamid of users
        Returns:
            User who has linked SteamOID profile with steamid
        """
        return User.query.join(SteamOID).filter(SteamOID.profile.has(steamid=steamid)).first()
