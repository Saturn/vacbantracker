from datetime import datetime

from flask import current_app, url_for, render_template
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature

from app.extensions import db, bcrypt
from app.steam.api import get_summaries_and_bans
from app.models.steam_oid import SteamOID
from app.models.profile import Profile
from app.models.tracking import Tracking
from app.email import send_email


def get_serializer(expiration=None):
    return Serializer(current_app.config['SECRET_KEY'], expiration)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    _password = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime, default=datetime.utcnow())
    verified = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(255))

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

    def track_profile(self, steamid, note=None):
        """
        Add profile for User to 'Track'
        Args:
            profile: The Profile to track
            note: An optional note for user to better track a profile
        Returns:
            True if user successfully tracks profile else False
        """
        return Tracking.track_profile(user=self, steamid=steamid, note=note)

    def untrack_profile(self, steamid):
        """
        Deletes tracking profile for steamid if user
        is currently tracking that profile.
        """
        return Tracking.untrack_profile(user=self, steamid=steamid)

    def get_tracking(self, steamids=None):
        """
        Return list of tracking profiles user is tracking.
        If steamids is None then will return all user tracking.
        """
        if steamids:
            return self.tracking.join(Profile)\
                                .filter(Profile.steamid.in_(steamids))\
                                .all()
        return self.tracking.all()

    def send_verification_email(self, email=None, email_type='welcome'):
        """
        Sends a verification email
        """
        if not email:
            email = self.email
        templates = {'welcome': 'email/welcome.txt',
                     'new': 'email/add_email.txt',
                     'change': 'email/change_email.txt',
                     'normal': 'email/verify.txt'}
        template = templates[email_type]
        token = self.generate_email_verification_token(email)
        url = url_for('auth.verify_email', token=token, _external=True)
        email_msg = render_template(template,
                                    url=url,
                                    email=email)
        send_email(email, 'Test', email_msg)
        print(email_msg)

    def change_email(self, new_email):
        self.email = new_email
        self.verified = False
        db.session.add(self)
        db.session.commit()

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
    def validate_email_token(token):
        response = {}
        user_id = None
        message = 'invalid'
        email = None
        try:
            data = get_serializer().loads(token)
            user_id = data.get('user_id')
            email = data.get('email')
            message = 'valid'
        except (BadSignature, SignatureExpired) as e:
            if type(e) is BadSignature:
                message = 'bad_signature'
            if type(e) is SignatureExpired:
                message = 'signature_expired'
        response['message'] = message
        response['user_id'] = user_id
        response['email'] = email
        return response

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
        validate = User.validate_email_token(token)
        if validate['message'] == 'valid':
            user = User.query.get(validate['user_id'])
            if user:
                email = validate.get('email')
                if email:
                    user.email = email
                    user.verified = True
                    db.session.add(user)
                    db.session.commit()
                    return 'verified'
            else:
                return 'unverified'  # user_id doesn't match any user
        return validate['message']

    def generate_forgot_password_token(self, expiration=3600):
        """
        Can only be used for non-steam accounts
        Args:
            expiration: Length of time in seconds the signed token is valid for
        Returns:
            Token which contains a user's id. Used to allow user to set password even
            when not logged in (forgotten password)
        """
        token = get_serializer(expiration).dumps({'user_id': self.id}).decode('utf-8')
        self.reset_token = token
        db.session.add(self)
        db.session.commit()
        return token

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
