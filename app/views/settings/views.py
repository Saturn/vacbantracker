from flask import Blueprint, render_template

from flask_login import current_user


settings = Blueprint('settings', __name__)


@settings.route('/settings')
def index():
    return render_template('settings.j2')
