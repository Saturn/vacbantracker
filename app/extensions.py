from flask_sqlalchemy import SQLAlchemy

from flask_login import LoginManager

from flask_bcrypt import Bcrypt

from flask_openid import OpenID


db = SQLAlchemy()

login_manager = LoginManager()

bcrypt = Bcrypt()

openid = OpenID()
