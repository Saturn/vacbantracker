import time
import os
import json
from unittest.mock import patch

import pytest
import requests_mock

from app.steam.api import PLAYER_BANS_URL, PLAYER_SUMMARIES_URL
from app import create_app, db


TEST_PATH = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def setup_app_and_db():
    app = create_app('testing')
    app.app_context = app.app_context()
    app.app_context.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    app.app_context.pop()


@pytest.fixture
def mock_steam():
    ban = summary = None
    data_dir = TEST_PATH + '/data/'
    with open(data_dir + 'ban.json', 'r') as f:
        ban = json.loads(f.read())
    with open(data_dir + 'summary.json', 'r') as f:
        summary = json.loads(f.read())

    mock = requests_mock.mock()
    mock.register_uri('GET',
                      PLAYER_BANS_URL,
                      json=ban)
    mock.register_uri('GET',
                      PLAYER_SUMMARIES_URL,
                      json=summary)
    return mock


@pytest.fixture
def mock_time():
    def _func(seconds):
        return patch('time.time', return_value=time.time() + seconds)
    return _func
