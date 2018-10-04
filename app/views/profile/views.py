
from flask import Blueprint, jsonify, request

from flask_login import login_required, current_user

from app.steam.id import is_steamid64
from app.models.profile import Profile


profile = Blueprint('profile', __name__)


@profile.route('/id/<steamid>')
def profile_view(steamid):
    return "This is the profile view"


@profile.route('/track', methods=('POST',))
@login_required
def track():
    steamid = request.form.get('steamid')
    note = request.form.get('note')
    if is_steamid64(steamid):
        tracked = current_user.track_profile(Profile.get(steamid), note)

    output = {'code': None, 'message': None}
    if tracked:
        output['code'] = 200
        output['message'] = 'Succesfully tracked profile.'
    else:
        output['code'] = 400
        output['message'] = 'Something went wrong.'
    return jsonify(output)


@profile.route('/untrack', methods=('POST',))
@login_required
def untrack():
    return "This is the untrack view"
