import re
from collections import OrderedDict

from flask import Blueprint, render_template, request, redirect, url_for

from flask_login import current_user

from app.steam.id import single_regex, SteamID, is_steamid64
from app.models.profile import Profile


search = Blueprint('search', __name__)


@search.route('/search', methods=('GET', 'POST'))
def search_view():
    if request.method == 'POST':
        """
        Get all steamids and redirect to a GET request
        where they can be retrieved and presented to user
        """
        data = request.form.get('steamids')
        data = data.replace('STEAM_1', 'STEAM_0')
        steamids = re.findall(single_regex, data)
        if not steamids:
            return redirect(url_for('search.search_view'))
        steamids = [SteamID(steamid).steamid64 for steamid in steamids]
        # remove non-unique steamids and maintain order of search
        steamids = list(OrderedDict.fromkeys(steamids).keys())[:50]
        steamids_query = ','.join(steamids)
        url = url_for('search.search_view') + '?steamids=' + steamids_query
        return redirect(url)

    if request.method == 'GET':
        steamids = request.args.get('steamids')
        profiles = None
        if steamids:
            steamids = steamids.split(',')
            steamids = [steamid for steamid in steamids if is_steamid64(steamid)]
            profiles = Profile.get_profiles(steamids)

            # if the user is logged in we need to check if they are
            # already tracking any profiles
            if current_user.is_authenticated:
                tracking = current_user.tracking.join(Profile)\
                                                .filter(Profile.steamid.in_(steamids))\
                                                .all()
                if tracking:
                    tracking = {x.steam_profile.steamid: x for x in tracking}
                    for profile in profiles:
                        if profile.steamid in tracking:
                            profile.tracking_info = tracking[profile.steamid]

        return render_template('search.j2', profiles=profiles)
