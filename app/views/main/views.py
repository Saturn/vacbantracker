from flask import Blueprint, render_template

from app.views.auth.forms import LoginForm


main = Blueprint('main', __name__)


@main.route('/')
def index():
    form = LoginForm()
    return render_template('index.j2', form=form)
