from datetime import datetime

from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

from app.extensions import db, bcrypt
from app.steam.api import get_summaries_and_bans
from app.models.steam_oid import SteamOID
from app.models.profile import Profile
from app.models.tracking import Tracking


def get_serializer(expiration=None):
    return Serializer(current_app.config['SECRET_KEY'], expiration)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime, default=datetime.utcnow())
    verified = db.Column(db.Boolean, default=False)

    steam_oid = db.relationship('SteamOID',
                                uselist=False,
                                cascade='all, delete-orphan')
    tracking = db.relationship('Tracking', lazy='dynamic', backref='user')

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password, rounds=8)

    def verify_pw(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def steam_user(self):
        return self.steam_oid is not None

    def __repr__(self):
        output = '<User {} [Normal] {}>'.format(self.id, self.email)
        if self.steam_oid:
            steamid = self.steam_oid.profile.steamid
            output = '<User {} [Steam] steamid={}>'.format(self.id, steamid)
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

    @staticmethod
    def get_or_create_steam_user(steamid):
        """
        If User with steamid already exists return that. If not, create
        new User with linked steam_oid account and profile.

        The user will not have an email yet if new.
        Args:
            steamid: The user's steamid got from steam openid
        Returns:
            The newly created or current steam User
        """
        steam_user = User.get_steam_user(steamid)
        if not steam_user:
            # all steam users also exist in profile table
            profile = Profile.get(steamid)
            if not profile:
                data = get_summaries_and_bans([steamid])[0]
                profile = Profile(**data)
            user = User()
            user.steam_oid = SteamOID()
            user.steam_oid.profile = profile
            db.session.add(user)
            db.session.commit()
            return user
        return steam_user

    def track_profile(self, profile, note=None):
        """
        Add profile for User to 'Track'
        Args:
            profile: The Profile to track
            note: An optional note for user to better track a profile
        Returns:
            True if user successfully tracks profile else False
        """
        # Make sure user is not already tracking profile or
        if self.steam_oid:  # user is a steam openid user
            if profile.steamid == self.steam_oid.profile.steamid:
                return False
        # that user is not trying to track themselves
        tracking = self.tracking.filter_by(profile=profile).first()
        if tracking:
            return False

        profile_data = dict(x_personaname=profile.personaname,
                            x_community_banned=profile.community_banned,
                            x_days_since_last_ban=profile.days_since_last_ban,
                            x_economy_ban=profile.economy_ban,
                            x_num_game_bans=profile.num_game_bans,
                            x_num_vac_bans=profile.num_vac_bans,
                            x_vac_banned=profile.vac_banned)
        tracking = Tracking(note=note,
                            profile=profile,
                            **profile_data)
        self.tracking.append(tracking)
        db.session.add(self)
        db.session.commit()
        return True

    def generate_email_verification_token(self, email=None, expiration=24*60*60):
        """
        Args:
            email: The user's email they wish to verify. If none then
            user the email that is linked to user
        Returns:
            Signed token [valid for 24 hours]
        """
        email = self.email if email is None else email
        if not email:
            raise ValueError('Must specify email')
        return get_serializer(expiration).dumps({'user_id': self.id,
                                                 'email': email})

    @staticmethod
    def validate_email(token=''):
        """
        Args:
            token: The token which contains an email address
        Returns:
            String indicating whether or not email has been verified.
                'verified' - email has been verified
                'unverified' - not been verified for unknown reason
                'bad_signature' - token had bad signature
                'signature_expired' - token's signature had expired (>24 hours)
        """
        try:
            data = get_serializer().loads(token)
            user_id = data.get('user_id')
            user = User.query.get(user_id)
            email = data.get('email')
            if email:
                user.email = email
                user.verified = True
                db.session.add(user)
                db.session.commit()
                return 'verified'
        except (BadSignature, SignatureExpired) as e:
            if isinstance(BadSignature, e):
                return 'bad_signature'
            if isinstance(SignatureExpired, e):
                return 'signature_expired'
        return 'unverified'

    def generate_forgot_password_token(self, expiration=3600):
        """
        Can only be used for non-steam accounts
        Args:
            expiration: Length of time in seconds the signed token is valid for
        Returns:
            Token which contains a user's id. Used to allow user to set password even
            when not logged in (forgotten password)
        """
        return get_serializer(expiration).dumps({'user_id': self.id})

    @staticmethod
    def validate_forgot_password_token(token=''):
        """
        Args:
            token: The token to verify. Contains a user_id
        Returns:
            The user_id or None.
        """
        try:
            data = get_serializer().loads(token)
            return data.get('user_id', None)
        except (BadSignature, SignatureExpired):
            return None
