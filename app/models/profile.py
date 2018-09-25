from app.extensions import db
from app.utils import unix_ts_to_dt
from app.steam.api import get_summaries_and_bans


class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steamid = db.Column(db.String(255), nullable=False)
    communityvisibilitystate = db.Column(db.Integer, nullable=False)
    profilestate = db.Column(db.Integer, nullable=False)
    personaname = db.Column(db.String(255))
    lastlogoff = db.Column(db.DateTime)
    profileurl = db.Column(db.String(255))
    avatar = db.Column(db.String(255))
    avatarmedium = db.Column(db.String(255))
    avatarfull = db.Column(db.String(255))
    personastate = db.Column(db.Integer, nullable=False)

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

    tracking = db.relationship('Tracking', backref='steam_profile', lazy='dynamic')

    # mapping of steam api key names to the Profile col names
    col_name_translation = {'CommunityBanned': 'community_banned',
                            'DaysSinceLastBan': 'days_since_last_ban',
                            'EconomyBan': 'economy_ban',
                            'NumberOfGameBans': 'num_game_bans',
                            'NumberOfVACBans': 'num_vac_bans',
                            'VACBanned': 'vac_banned'}

    def __init__(self, **kwargs):
        """
        Make api data match column names on profile table
        and convert unix timestamps to datetime objects
        """
        translations = Profile.col_name_translation
        for key in translations:
            if key in kwargs:
                kwargs[translations[key]] = kwargs.pop(key)
        if 'lastlogoff' in kwargs:
            kwargs['lastlogoff'] = unix_ts_to_dt(kwargs['lastlogoff'])
        if 'timecreated' in kwargs:
            kwargs['timecreated'] = unix_ts_to_dt(kwargs['timecreated'])
        # sometimes profilestate not set
        if 'profilestate' not in kwargs:
            kwargs['profilestate'] = 0
        self.__dict__.update(kwargs)

    @staticmethod
    def update_profile(profile, new_data):
        translations = Profile.col_name_translation
        for key in translations:
            if key in new_data:
                new_data[translations[key]] = new_data.pop(key)
        if 'lastlogoff' in new_data:
            new_data['lastlogoff'] = unix_ts_to_dt(new_data['lastlogoff'])
        if 'timecreated' in new_data:
            new_data['timecreated'] = unix_ts_to_dt(new_data['timecreated'])
        profile.__dict__.update(new_data)
        return profile

    @staticmethod
    def get_profiles(list_of_steamids):
        """
        Args:
            list_of_steamids: steamids to get (int)
        Returns:
            list of Profile objects
        """
        api_data = get_summaries_and_bans(list_of_steamids)
        all_steamids = set(list_of_steamids)
        existing_profiles = Profile.query.filter(Profile.steamid.in_(all_steamids))\
                                         .all()
        already_existing = {}
        for profile in existing_profiles:
            already_existing[profile.steamid] = profile
        already_existing_ids = already_existing.keys()
        data = []
        for acc in api_data:
            if acc['steamid'] not in already_existing_ids:
                data.append(Profile(**acc))
            else:
                profile = already_existing[acc['steamid']]
                profile = Profile.update_profile(profile, acc)
                data.append(profile)
        db.session.add_all(data)
        db.session.commit()
        # slow sorting
        # data.sort(key=lambda x: list_of_steamids.index(int(x.steamid)))
        sort_order = {v: i for i, v in enumerate(list_of_steamids)}
        data.sort(key=lambda x: sort_order[int(x.steamid)])
        return data

    @staticmethod
    def get(steamid):
        """
        Args:
            steamid: The steamid we want to fetch
        Returns:
            Profile for steamid
        """
        return Profile.query.filter_by(steamid=steamid).first()

    def __repr__(self):
        return '<Profile steamid={}>'.format(self.steamid)
