import os
import sys

from app import create_app, db


app = create_app('default')


@app.shell_context_processor
def make_shell_context():
    return dict(app=app,
                db=db)
