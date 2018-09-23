from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length


password_validation = [Length(min=8, message='Password must be at least 8 characters.'),
                       DataRequired()]


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=password_validation)
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=password_validation)
    submit = SubmitField('Register')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class NewPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=password_validation)
    submit = SubmitField('Save New Password')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('Current Password', validators=password_validation)
    new_password = PasswordField('New Password', validators=password_validation)
    submit = SubmitField('Change Password')
