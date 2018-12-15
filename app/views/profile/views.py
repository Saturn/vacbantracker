import re

from flask import Blueprint, request, Response, json, render_template, abort
from flask_login import login_required, current_user
from sqlalchemy import desc, asc

from app.steam.id import is_steamid64
from app.models.profile import Profile
from app.models.tracking import Tracking


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
    def parse_page_query():
        page = request.args.get('page', '1')
        page_regex = re.compile('(\d)')
        page_qs = page_regex.match(page)
        if page_qs:
            page = int(page)
            return page
        return abort(404)

    def parse_sort_query():
        sort_col_lookup = {'vac': Profile.vac_banned,
                           'date': Tracking.timetracked,
                           'name': Profile.personaname}
        sort_regex = re.compile('([\+\-])(vac|date|name)')
        sort_col = sort_col_lookup['date']
        sort_order = asc
        sort = request.args.get('sort', '')

        sort_qs = sort_regex.match(sort)
        if sort_qs:
            sort_order = asc if sort_qs.group(1) == '+' else desc
            sort_col = sort_col_lookup[sort_qs.group(2)]
        return sort_order, sort_col

    page = parse_page_query()
    sort_order, sort_col = parse_sort_query()

    tracking = current_user.tracking.join(Profile)\
                                    .order_by(sort_order(sort_col))\
                                    .paginate(page, 25)\
                                    .items

    return render_template('tracking.j2',
                           tracking=tracking)
