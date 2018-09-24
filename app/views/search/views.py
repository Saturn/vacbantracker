import re
from collections import OrderedDict

from flask import Blueprint, render_template, request, redirect, url_for

from flask_login import current_user

from app.steam.id import single_regex, SteamID


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
        steamids = [SteamID(steamid).steamid64 for steamid in steamids]
        # remove non-unique steamids and maintain order of search
        steamids = list(OrderedDict.fromkeys(steamids).keys())[:100]
        steamids_query = ','.join(steamids)
        url = url_for('search.search_view') + '?steamids=' + steamids_query
        return redirect(url)

    if request.method == 'GET':
        return request.args.get('steamids')
