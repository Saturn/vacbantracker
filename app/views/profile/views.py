from flask import Blueprint, request, Response, json, render_template
from flask_login import login_required, current_user
from sqlalchemy import asc, desc

from app.steam.id import is_steamid64
from app.models.profile import Profile
from app.models.tracking import Tracking

from app.views.profile.utils import (parse_page_query, parse_sort_query,
                                     get_tracking_sort_by_urls)


profile = Blueprint('profile', __name__)


@profile.route('/id/<steamid>')
def profile_view(steamid):
    profile = None
    tracking = None
    if current_user.is_authenticated:
        tracking = current_user.get_tracking([steamid])
        if tracking:
            tracking = tracking[0]  # user.get_tracking returns list
    if is_steamid64(str(steamid)):
        profile = Profile.get_profile(steamid)
    return render_template('profile.j2',
                           profile=profile,
                           tracking=tracking)


@profile.route('/track', methods=('POST',))
@login_required
def track():
    steamid = request.form.get('steamid')
    note = request.form.get('note')
    tracked = None
    if is_steamid64(str(steamid)):
        tracked = current_user.track_profile(steamid, note)

    if tracked:
        code = 200
        message = 'Succesfully tracked profile.'
    else:
        code = 400
        message = 'Something went wrong.'
    data = json.dumps(dict(message=message, code=code))
    return Response(data, status=code, mimetype='application/json')


@profile.route('/untrack', methods=('POST',))
@login_required
def untrack():
    steamid = request.form.get('steamid')
    if is_steamid64(str(steamid)):
        untracked_profile = current_user.untrack_profile(steamid)
    if untracked_profile:
        code = 200
        message = 'Succesfuly untracked profile.'
    else:
        code = 400
        message = 'Something went wrong.'
    data = json.dumps(dict(message=message, code=code))
    return Response(data, status=code, mimetype='application/json')


@profile.route('/tracking')
@login_required
def tracking():
    page = parse_page_query()
    _sort_by, _sort_direction = parse_sort_query()

    sort_col_lookup = {'vac': Profile.vac_banned,
                       'date': Tracking.timetracked,
                       'name': Profile.personaname}
    sort_by = sort_col_lookup[_sort_by]
    sort_direction = desc if _sort_direction == 'desc' else asc

    tracking = current_user.tracking.join(Profile)\
                                    .order_by(sort_direction(sort_by))\
                                    .paginate(page, 25)\
                                    .items
    sort_urls = get_tracking_sort_by_urls(_sort_direction, _sort_by)
    return render_template('tracking.j2',
                           tracking=tracking,
                           base_url='/tracking',
                           sort_urls=sort_urls)
