from flask import Blueprint, render_template

from flask_login import current_user

search = Blueprint('search', __name__)


@search.route('/search')
def index():
    return "Search view!"
    return render_template('search.j2')
