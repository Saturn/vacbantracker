
from flask import Blueprint, request, Response, json, render_template, flash

from flask_login import login_required, current_user

from app.steam.id import is_steamid64
from app.models.profile import Profile


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
        profile = Profile.get_profiles([steamid])[0]
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
        flash('You are now tracking steamid:{}'.format(steamid))
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
        flash('You are no longer tracking steamid:{}'.format(steamid))
    else:
        code = 400
        message = 'Something went wrong.'
    data = json.dumps(dict(message=message, code=code))
    return Response(data, status=code, mimetype='application/json')
