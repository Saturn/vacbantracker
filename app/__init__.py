from flask import Flask

from app.config import config
from app.extensions import db, login_manager, bcrypt, openid

from app.views.main.views import main
from app.views.auth.views import auth
from app.views.search.views import search
from app.views.profile.views import profile
from app.views.settings.views import settings


def register_blueprints(app):
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(search)
    app.register_blueprint(profile)
    app.register_blueprint(settings)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    openid.init_app(app)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)

    return app
