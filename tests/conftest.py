import time
import os
import json
from unittest.mock import patch

import pytest
import requests_mock

from app.steam.api import PLAYER_BANS_URL, PLAYER_SUMMARIES_URL
from app import create_app, db


TEST_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = TEST_PATH + '/data/'


def get_ban_data():
    with open(DATA_PATH + 'ban.json', 'r') as f:
        return json.loads(f.read())


def get_summary_data():
    with open(DATA_PATH + 'summary.json', 'r') as f:
        return json.loads(f.read())


def get_bans_data():
    with open(DATA_PATH + 'bans.json', 'r') as f:
        return json.loads(f.read())


def get_summaries_data():
    with open(DATA_PATH + 'summaries.json', 'r') as f:
        return json.loads(f.read())


def get_requests_mock(multiple=False):
    if multiple:
        ban = get_bans_data()
        summary = get_summaries_data()
    else:
        ban = get_ban_data()
        summary = get_summary_data()
    mock = requests_mock.mock()
    mock.register_uri('GET',
                      PLAYER_BANS_URL,
                      json=ban)
    mock.register_uri('GET',
                      PLAYER_SUMMARIES_URL,
                      json=summary)
    return mock


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
def mock_steam_single():
    return get_requests_mock(multiple=False)


@pytest.fixture
def mock_steam_multiple():
    return get_requests_mock(multiple=True)


@pytest.fixture
def steamid():
    return '76561198066693739'


@pytest.fixture
def steamids():
    return ['76561197960359452',
            '76561198034202275',
            '76561197988627193',
            '76561197987713664',
            '76561197982036918']


@pytest.fixture
def mock_time():
    def _func(seconds):
        return patch('time.time', return_value=time.time() + seconds)
    return _func
