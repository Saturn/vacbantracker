from flask import Flask

from app.config import config
from app.extensions import db, login_manager

from app.blueprints.main.views import main


def register_blueprints(app):
    app.register_blueprint(main)


def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)

    return app
