import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    MAILGUN_API_URL = os.environ.get('MAILGUN_API_URL')
    MAIL_GUN_API_KEY = os.environ.get('MAIL_GUN_API_KEY')
    EMAIL_FROM = os.environ.get('EMAIL_FROM')
    STEAM_API_KEY = os.environ.get('STEAM_API_KEY')
    SITE_TITLE = "VACBanTracker"
    SECRET_KEY = 'This is the flask secret key'
    WTF_CSRF_SECRET_KEY = 'This is the wtf csrf secret key'


class DevelopmentConfig(BaseConfig):
    HOST = '0.0.0.0'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'dev.db')
    WTF_CSRF_ENABLED = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'testing.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir, 'data.db')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
