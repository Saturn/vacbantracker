from datetime import datetime, timedelta

from app.extensions import db
from app.utils import unix_ts_to_dt
from app.steam.api import get_summaries_and_bans
from app.steam.id import SteamID, VANITY_REGEX


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.String(255), nullable=False, unique=True)
    steamid_ = db.Column(db.String(255), nullable=False)
    steamid3 = db.Column(db.String(255), nullable=False)
    communityvisibilitystate = db.Column(db.Integer, nullable=False)
    profilestate = db.Column(db.Integer, nullable=False)
    personaname = db.Column(db.String(255))
    lastlogoff = db.Column(db.DateTime)
    profileurl = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    avatarmedium = db.Column(db.String(255))
    avatarfull = db.Column(db.String(255))
    personastate = db.Column(db.Integer, nullable=False)

    time_added = db.Column(db.DateTime, default=datetime.utcnow())
    time_updated = db.Column(db.DateTime, default=datetime.utcnow())

    # optional
    commentpermission = db.Column(db.Integer)
    realname = db.Column(db.String(255))
    primaryclanid = db.Column(db.String(255))
    timecreated = db.Column(db.DateTime)
    loccountrycode = db.Column(db.String(255))
    locstatecode = db.Column(db.String(255))
    loccityid = db.Column(db.Integer)
    gameid = db.Column(db.String(255))
    gameextrainfo = db.Column(db.String(255))
    gameserverip = db.Column(db.String(255))

    # ban info
    community_banned = db.Column(db.Boolean)
    days_since_last_ban = db.Column(db.Integer)
    economy_ban = db.Column(db.String(255))
    num_game_bans = db.Column(db.Integer)
    num_vac_bans = db.Column(db.Integer)
    vac_banned = db.Column(db.Boolean)

    tracking = db.relationship('Tracking',
                               backref='steam_profile',
                               lazy='dynamic')

    # mapping of steam api key names to the Profile col names
    col_name_translation = {'CommunityBanned': 'community_banned',
                            'DaysSinceLastBan': 'days_since_last_ban',
                            'EconomyBan': 'economy_ban',
                            'NumberOfGameBans': 'num_game_bans',
                            'NumberOfVACBans': 'num_vac_bans',
                            'VACBanned': 'vac_banned'}

    def __init__(self, **kwargs):
        self = Profile.apply_data_to_profile(self, kwargs)

    @staticmethod
    def update_profile(profile, new_data):
        return Profile.apply_data_to_profile(profile, new_data)

    @staticmethod
    def apply_data_to_profile(the_profile, data):
        """
        Return profile with data applied to columns
        Apply column translations
        Some steam profile attributes are optional
        """
        data = Profile.apply_col_translations(data)
        if 'lastlogoff' in data:
            data['lastlogoff'] = unix_ts_to_dt(data['lastlogoff'])
        if 'timecreated' in data:
            data['timecreated'] = unix_ts_to_dt(data['timecreated'])
        if 'profilestate' not in data:
            data['profilestate'] = 0
        if not the_profile.steamid_:
            s = SteamID(data['steamid'])
            data['steamid_'] = s.steamid
            data['steamid3'] = s.steamid3
        the_profile.__dict__.update(data)
        the_profile.time_updated = datetime.utcnow()
        return the_profile

    @staticmethod
    def apply_col_translations(data):
        """
        Args:
            data Steam API data
        Returns:
            The Steam API data with key names matching Profile model
        """
        translations = Profile.col_name_translation
        for key in translations:
            if key in data:
                data[translations[key]] = data.pop(key)
        return data

    @staticmethod
    def get_profiles(list_of_steamids):
        """
        Args:
            list_of_steamids: steamids to get (int)
        Returns:
            list of Profile objects

        Doesn't fetch from API if all profiles are <30 mins old
        """
        all_steamids = set(list_of_steamids)
        existing_profiles = Profile.query.filter(Profile.steamid.in_(all_steamids))\
                                         .all()

        # if all profiles exist and were updated less than 30 mins ago
        # then do not fetch api data. Just serve old data.
        fetch = True
        time_window = datetime.utcnow() - timedelta(minutes=30)
        is_fresh = (x.time_updated > time_window for x in existing_profiles)
        if len(existing_profiles) == len(list_of_steamids):
            if all(is_fresh):
                fetch = False

        if fetch:
            api_data = get_summaries_and_bans(list_of_steamids)
            already_existing = {x.steamid: x for x in existing_profiles}
            data = []
            for acc in api_data:
                if acc['steamid'] not in already_existing:
                    data.append(Profile(**acc))
                else:
                    profile = already_existing[acc['steamid']]
                    profile = Profile.update_profile(profile, acc)
                    data.append(profile)
        else:
            data = existing_profiles

        db.session.add_all(data)
        db.session.commit()

        sort_order = {v: i for i, v in enumerate(list_of_steamids)}
        data.sort(key=lambda x: sort_order[x.steamid])
        return data

    @staticmethod
    def get_profile(steamid):
        return Profile.get_profiles([steamid])[0]

    @staticmethod
    def get(steamid):
        """
        Args:
            steamid: The steamid we want to fetch
        Returns:
            Profile for steamid
        """
        return Profile.query.filter_by(steamid=steamid).first()

    def get_privacy(self):
        states = {1: 'Private',
                  2: 'Friends Only',
                  3: 'Friends of Friends',
                  4: 'Users Only',
                  5: 'Public'}
        return states.get(self.communityvisibilitystate, 'Unknown')

    @property
    def steamurl(self):
        return 'https://steamcommunity.com/profiles/{}'.format(self.steamid)

    @property
    def vanityurl(self):
        vanity = VANITY_REGEX.match(self.profileurl)
        return self.profileurl if vanity else None

    def __repr__(self):
        return '<Profile steamid: {}>'.format(self.steamid)
