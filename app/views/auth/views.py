import re

from flask import Blueprint, redirect, url_for, render_template, flash

from flask_login import current_user, logout_user, login_user

from app.extensions import openid, db
from app.models.user import User

from .forms import (LoginForm,
                    RegisterForm,
                    ChangePasswordForm,
                    ForgotPasswordForm)


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user and user.verify_pw(password):
            login_user(user, form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email/password', 'danger')
    return render_template('login.j2', form=form)


@auth.route('/register', methods=('GET', 'POST'))
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data
        user = User(email=email,
                    password=password)
        db.session.add(user)
        db.session.commit()
        # email token here
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('register.j2', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@auth.route('/forgot_password')
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        # send token to email
        pass
    return 'This is the forgot password route!'


@auth.route('/new_password')
def new_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        # save user new password and redirect
        # to login screen
        pass
    return 'This is the new password route!'


@auth.route('/login/steam')
@openid.loginhandler
def login_with_steam():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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
    if steamid:
        user = User.get_or_create_steam_user(steamid)
        login_user(user)
    return redirect(url_for('main.index'))
