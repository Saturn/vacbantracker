from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError

from app.models.user import User


password_validation = [Length(min=8, message='Password must be at least 8 characters.'),
                       DataRequired()]
equal1 = [EqualTo('password', 'Password\'s do not match.')]
equal2 = [EqualTo('password2', 'Password\'s do not match.')]
password1_validation = password_validation + equal1
password2_validation = password_validation + equal2


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=password_validation)
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=password2_validation)
    password2 = PasswordField('Confirm Password', validators=password1_validation)
    submit = SubmitField('Register')

    def validate_email(self, field):
        query = User.query.with_entities(User.email)\
                          .filter_by(email=field.data.lower())\
                          .first()
        if query:
            raise ValidationError('Email already in use.')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send password reset email')

    def validate_email(self, field):
        if not User.query.with_entities(User.email)\
                         .filter_by(email=field.data.lower())\
                         .first():
            raise ValidationError('An account with that email address does not exist.')


class NewPasswordForm(FlaskForm):
    token = HiddenField(validators=[DataRequired()])
    password = PasswordField('New Password', validators=password2_validation)
    password2 = PasswordField('Confirm New Password', validators=password1_validation)
    submit = SubmitField('Save New Password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=password_validation)
    password = PasswordField('New Password', validators=password2_validation)
    password2 = PasswordField('Confirm New Password', validators=password1_validation)
    submit = SubmitField('Change Password')
