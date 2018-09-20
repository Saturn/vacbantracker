import re

from flask import Blueprint, redirect, url_for

from flask_login import current_user, logout_user, login_user, login_required

from app.extensions import openid


auth = Blueprint('auth', __name__)


@auth.route('/login')
def index():
    return 'This is the login route!'


@auth.route('/register')
def register():
    return 'This is the register route!'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/login_with_steam')
@openid.loginhandler
def login_with_steam():
    if current_user.is_authenticated:
        return redirect(openid.get_next_url())
    return openid.try_login('https://steamcommunity.com/openid')


@openid.after_login
def after_steam_login(resp):
    """
    If steam user is new then create new user account and attach
    a new steam openid instance.
    If steam user is not new then log them in
    """
    match = re.search('steamcommunity.com/openid/id/(.*?)$', resp.identity_url)
    steamid = match.group(1)
    return redirect(openid.get_next_url())
