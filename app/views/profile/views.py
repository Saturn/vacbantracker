
from flask import Blueprint, request, Response, json, render_template, flash

from flask_login import login_required, current_user

from app.steam.id import is_steamid64
from app.models.profile import Profile


profile = Blueprint('profile', __name__)


@profile.route('/id/<steamid>')
def profile_view(steamid):
    profile = None
    if is_steamid64(str(steamid)):
        profile = Profile.get_profiles([steamid])[0]
    return render_template('profile.j2', profile=profile)


@profile.route('/track', methods=('POST',))
@login_required
def track():
    steamid = request.form.get('steamid')
    note = request.form.get('note')
    tracked = None
    if is_steamid64(str(steamid)):
        tracked = current_user.track_profile(Profile.get(steamid), note)

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
    return "This is the untrack view"
