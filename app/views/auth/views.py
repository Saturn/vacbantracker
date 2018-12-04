import re

from flask import Blueprint, redirect, url_for, render_template, flash, request

from flask_login import current_user, logout_user, login_user, login_required

from app.extensions import openid, db
from app.models.user import User

from .forms import (LoginForm,
                    RegisterForm,
                    ChangePasswordForm,
                    ForgotPasswordForm,
                    NewPasswordForm,
                    ChangeEmailForm,
                    AddEmailForm)


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=('GET', 'POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower())\
                         .first()
        if user and not user.steam_user:
            login_user(user, form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email/password', 'danger')
    return render_template('login.j2', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


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
        user.send_verification_email()
        flash(('Welcome. An email verification message '
               'has been sent to {}'.format(email)), 'success')
        login_user(user)
        return redirect(url_for('main.index'))
    return render_template('register.j2', form=form)


@auth.route('/resend')
@login_required
def resend():
    current_user.send_verification_email(email_type='normal')
    flash('Verification email has been sent to {}'.format(current_user.email), 'success')
    return redirect(url_for('auth.settings_index'))


@auth.route('/verify')
def verify_email():
    token = request.args.get('token')
    status = User.validate_email(token)
    if status == 'verified':
        flash('Succesfully verified email address', 'success')
    else:
        flash('Invalid verification token', 'danger')
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
            email_msg = render_template('email/forgot_password.txt',
                                        email=user.email,
                                        url=url)
            print(email_msg)
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
            # make sure token is same as 'current' user token
            if token == user.reset_token:
                user.password = form.password.data
                user.reset_token = ''
                db.session.add(user)
                db.session.commit()
                flash('Successfully reset password. Please login.', 'success')
                return redirect(url_for('auth.login'))
    else:
        flash('Invalid token.', 'danger')
        return redirect(url_for('main.index'))
    return render_template('new_password.j2', form=form)


@auth.route('/settings', methods=('GET', 'POST'))
@login_required
def settings_index():
    """
    There is two different email forms.
    One for changing a currently set email (for normal and steam accounts)
    and another for setting an email for a steam account that has never
    set one before.
    """
    pw_form = ChangePasswordForm(prefix='pw')
    pw_form.current_user = current_user  # so we can validate users password
    email_form = ChangeEmailForm()


    if pw_form.submit.data and pw_form.validate_on_submit():
        current_user.password = pw_form.password.data
        db.session.add(current_user)
        db.session.commit()
        flash('Successfully changed password.', 'success')

    elif email_form.submit.data and email_form.validate_on_submit():
        new_email = email_form.email.data.lower()
        current_user.send_verification_email(new_email, email_type='new')
        flash('Email verification has been sent to ' + new_email, 'success')
        current_user.change_email(new_email)

    add_email_form = None
    if current_user.steam_user and not current_user.email:
        add_email_form = AddEmailForm(prefix='add')

        if add_email_form.submit.data and add_email_form.validate_on_submit():
            new_email = add_email_form.email.data.lower()
            current_user.send_verification_email(new_email, email_type='new')
            flash('Email verification has been sent to ' + new_email, 'success')
            current_user.change_email(new_email)

    return render_template('settings.j2',
                           pw_form=pw_form,
                           email_form=email_form,
                           add_email_form=add_email_form)


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
