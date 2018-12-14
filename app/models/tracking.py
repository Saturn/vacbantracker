from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.profile import Profile


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

    __table_args__ = (UniqueConstraint('profile_id', 'user_id'),)

    def __repr__(self):
        return '<Tracking steamid: {} user: {}>'.format(self.profile.steamid,
                                                        self.user.id)

    @staticmethod
    def track_profile(user, steamid, note=None):
        """
        Add profile for User to 'Track'
        Args:
            profile: The Profile to track
            note: An optional note for user to better track a profile
        Returns:
            True if user successfully tracks profile else False
        """
        profile = Profile.get(steamid)

        if user.steam_oid:
            if profile.steamid == user.steam_oid.profile.steamid:
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
        try:
            user.tracking.append(tracking)
            db.session.add(user)
            db.session.commit()
            return True
        except IntegrityError:
            return False

    @staticmethod
    def untrack_profile(user, steamid):
        """
        Deletes tracking profile for steamid if user
        is currently tracking that profile.
        """
        tracking = user.tracking.join(Profile)\
                                .filter(Profile.steamid == steamid)\
                                .first()
        if tracking:
            db.session.delete(tracking)
            db.session.commit()
            return True
        return False
