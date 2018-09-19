from flask import Blueprint

auth = Blueprint('auth', __name__)


@auth.route('/login')
def index():
    return 'This is the login route!'


@auth.route('/register')
def register():
    return 'This is the register route!'
