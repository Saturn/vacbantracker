
from flask import Blueprint, jsonify, request, Response, json

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
    return "This is the untrack view"
