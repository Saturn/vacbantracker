from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.extensions import db, bcrypt
from app.models.steam_oid import SteamOID


def get_serializer(expiration=None):
    return Serializer(current_app.config['SECRET_KEY'], expiration)


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
        return User.query.join(SteamOID)\
                         .filter(SteamOID.profile.has(steamid=steamid)).first()

    def generate_email_verification_token(self, email=None, expiration=24*60*60):
        """
        Args:
            email: The user's email they wish to verify. If none then
            user the email that is linked to user
        Returns:
            Signed token [valid for 24 hours]
        """
        email = self.email if email is None else email
        return get_serializer(expiration).dumps({'user_id': self.id,
                                                 'email': email})
