
from flask import Blueprint

from flask_login import login_required


profile = Blueprint('profile', __name__)


@profile.route('/id/<steamid>')
def profile_view(steamid):
    return "This is the profile view"


@profile.route('/track', methods=('POST',))
@login_required
def track():
    return "This is the track view"


@profile.route('/untrack', methods=('POST',))
@login_required
def untrack():
    return "This is the untrack view"
