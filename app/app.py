import os
import sys

from app import create_app, db

from app.models.user import User

app = create_app('default')


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db,
                User=User)
