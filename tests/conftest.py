# flake8: noqa
# pylint: disable=redefined-outer-name
import pickle
import os
import json
from collections import namedtuple
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nhltv_lib.models import Base


@pytest.fixture(scope="function", autouse=True)
def mock_db_session(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all(engine)
    session.commit()
    monkeypatch.setattr("nhltv_lib.db_session.session", session)
    return session


@pytest.fixture
def parsed_args():
    return namedtuple(
        "Arguments",
        [
            "team",
            "username",
            "password",
            "download_folder",
            "checkinterval",
            "retentiondays",
            "days_back_to_search",
            "shorten_video",
            "debug_dumps_enabled",
        ],
    )


@pytest.fixture
def parsed_args_list():
    return [
        "CHI",  # 0 team
        "username",  # 1
        "password",  # 2
        os.getcwd() + "/test",  # 3 dl folder
        "10",  # 4 checkinterval
        "4",  # 5 days to keep
        "2",  # 6 days back to search
        False,  # 7 shorten video
        False,  # 8 debug dumps
    ]


@pytest.fixture
def parsed_arguments(parsed_args, parsed_args_list):
    return parsed_args(*parsed_args_list)


@pytest.fixture
def arguments_list():
    return [
        "--team",
        "NSH",
        "--username",
        "username",
        "--password",
        "password",
        "-i",
        "4",
        "--download_folder",
        os.getcwd() + "/test",
        "--keep",
        "5",
    ]


@pytest.fixture
def teams_data():
    with open("tests/data/teams.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="function", autouse=True)
def mocked_fetch_teams(mocker, teams_data):
    return mocker.patch("nhltv_lib.teams.fetch_teams", return_value=teams_data)


@pytest.fixture
def games_data():
    with open("tests/data/games.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="function", autouse=True)
def mocked_fetch_games(mocker, games_data):
    return mocker.patch("nhltv_lib.game.fetch_games", return_value=games_data)


@pytest.fixture(scope="function", autouse=True)
def mocked_parse_args(mocker, parsed_arguments):
    return mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )


@pytest.fixture(scope="function", autouse=True)
def mock_os_path_exists(mocker):
    return mocker.patch("os.path.exists", return_value=True)


@pytest.fixture(scope="function", autouse=True)
def mock_os_remove(mocker):
    return mocker.patch("os.remove")


@pytest.fixture(scope="function", autouse=True)
def mock_os_path_isdir(mocker):
    return mocker.patch("os.path.isdir", return_value=True)


@pytest.fixture
def fake_stream_json():
    with open("tests/data/stream.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_session_json():
    with open("tests/data/session.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_silencedetect_output():
    with open("tests/data/silencedetect_output.txt", "rb") as f:
        return f.readlines()


@pytest.fixture
def fake_games():
    with open("tests/data/games_pickle", "rb") as f:
        return pickle.load(f)


@pytest.fixture
def fake_download():
    with open("tests/data/download_pickle", "rb") as f:
        return pickle.load(f)
