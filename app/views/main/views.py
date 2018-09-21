from flask import Blueprint, render_template

from flask_login import current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    if current_user.is_authenticated and current_user.steam_oid:
        return 'Hi, {}'.format(current_user.steam_oid.profile.steamid)
    return render_template('base.jinja2')
