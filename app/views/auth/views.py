import re

from flask import Blueprint, redirect, url_for, render_template, flash, request

from flask_login import current_user, logout_user, login_user

from app.extensions import openid, db
from app.models.user import User

from .forms import (LoginForm,
                    RegisterForm,
                    ChangePasswordForm,
                    ForgotPasswordForm,
                    NewPasswordForm)


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


@auth.route('/forgot_password', methods=('GET', 'POST'))
def forgot_password():
    """
    Sends email token which will contain link so user can
    reset their password.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_forgot_password_token()
            # email token here
            url = url_for('auth.new_password', token=token, _external=True)
            email = render_template('email/forgot_password.txt',
                                    email=user.email,
                                    url=url)
            print(email)
            flash('A password reset token has been sent.', 'success')
            return redirect(url_for('main.index'))
    return render_template('forgot_password.j2', form=form)


@auth.route('/new_password', methods=('GET', 'POST'))
def new_password():
    """
    Validates password reset token and if it is valid
    presents user with form to set a new password.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = NewPasswordForm()

    # we get token from querystring the first time (get)
    # this gets added to the form as a hidden field
    # for additional post requests
    token = request.args.get('token') or request.form.get('token')
    # token is valid if this returns user_id from token
    user_id = User.validate_forgot_password_token(token)
    if user_id:
        form.token.data = token
        if form.validate_on_submit():
            user = User.query.get(user_id)
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Successfully reset password. Please login.', 'success')
            return redirect(url_for('auth.login'))
    else:
        flash('Invalid token.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('new_password.j2', form=form)


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
