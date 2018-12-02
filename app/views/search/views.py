from flask import Blueprint, render_template, request, redirect, url_for

from flask_login import current_user

from app.steam.id import is_steamid64, extract_steamids
from app.models.profile import Profile


search = Blueprint('search', __name__)


@search.route('/search', methods=('GET', 'POST'))
def search_view():
    if request.method == 'POST':
        """
        Get all steamids and redirect to a GET request
        where they can be retrieved and presented to user
        """
        steamid_input = request.form.get('steamids')
        steamids = extract_steamids(steamid_input)
        steamids_query = ','.join(steamids)
        url = url_for('search.search_view') + '?steamids=' + steamids_query
        return redirect(url)

    if request.method == 'GET':
        steamids = request.args.get('steamids')
        profiles = None
        if steamids:
            steamids = steamids.split(',')
            steamids = list(filter(is_steamid64, steamids))
            profiles = Profile.get_profiles(steamids)

            # if the user is logged in we need to check if they are
            # already tracking any profiles
            if current_user.is_authenticated:
                user_tracking = current_user.tracking
                tracking = user_tracking.join(Profile)\
                                        .filter(Profile.steamid.in_(steamids))\
                                        .all()
                if tracking:
                    tracking = {x.steam_profile.steamid: x for x in tracking}
                    for profile in profiles:
                        if profile.steamid in tracking:
                            profile.tracking_info = tracking[profile.steamid]
            # if only 1 steamid in search then redirect to profile page
            if len(profiles) == 1:
                return redirect(url_for('profile.profile_view',
                                        steamid=profiles[0].steamid))

        return render_template('search.j2', profiles=profiles)
