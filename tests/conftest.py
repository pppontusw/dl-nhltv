# flake8: noqa
# pylint: disable=redefined-outer-name
import pickle
import os
import json
from collections import namedtuple
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from nhltv_lib.game import Game
from nhltv_lib.models import Base


@pytest.fixture(scope="function", autouse=True)
def mock_progress_bar(mocker):
    mocker.patch("nhltv_lib.download.print_progress_bar")


@pytest.fixture(scope="function", autouse=True)
def mock_db_session(monkeypatch):
    engine = create_engine("sqlite://")
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    Base.metadata.create_all()
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
            "quality",
            "download_folder",
            "checkinterval",
            "retentiondays",
            "days_back_to_search",
            "shorten_video",
            "debug_dumps_enabled",
            "preferred_stream",
            "no_progress_bar",
        ],
    )


@pytest.fixture
def parsed_args_list():
    return [
        "NSH",  # 0 team
        "username",  # 1
        "password",  # 2
        "3333",  # 3 quality
        os.getcwd() + "/test",  # 4 dl folder
        "10",  # 5 checkinterval
        "4",  # 6 days to keep
        "2",  # 7 days back to search
        False,  # 8 shorten video
        False,  # 9 debug dumps
        ["FS-TN"],  # 10 preferred_stream
        False,  # 11 no_progress_bar
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
        "--quality",
        "3333",
        "-i",
        "4",
        "--download_folder",
        os.getcwd() + "/test",
        "--keep",
        "5",
        "--prefer-stream",
        "FS-TN",
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
def mocked_dllog_contents(mocker, fake_download_log_fail):
    return mocker.patch(
        "nhltv_lib.download._get_dllog_contents",
        return_value=fake_download_log_fail,
    )


@pytest.fixture(scope="function", autouse=True)
def mocked_dlfile_contents(mocker, fake_download_file_fail):
    return mocker.patch(
        "nhltv_lib.download._get_downloadfile_contents",
        return_value=fake_download_file_fail,
    )


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
def fake_game_objects(games_data):
    games = games_data["dates"][0]["games"]
    return tuple(
        Game(i["gamePk"], True, i["content"]["media"]["epg"][0]["items"])
        for i in games
    )


@pytest.fixture
def fake_stream_json():
    with open("tests/data/stream.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_decode_hashes():
    with open("tests/data/decode_hashes.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_session_json():
    with open("tests/data/session.json", "r") as f:
        return json.load(f)


@pytest.fixture
def fake_master_file():
    with open("tests/data/master.m3u8", "r") as f:
        return f.read()


@pytest.fixture
def fake_quality_file():
    with open("tests/data/input.m3u8", "r") as f:
        return f.readlines()


@pytest.fixture
def fake_download_file():
    with open("tests/data/download_file.txt", "r") as f:
        return f.readlines()


@pytest.fixture
def fake_download_file_fail():
    with open("tests/data/download_file_fail.txt", "r") as f:
        return f.readlines()


@pytest.fixture
def fake_download_log_fail():
    with open("tests/data/download_log_fail.log", "r") as f:
        return f.readlines()


@pytest.fixture
def fake_concat_file():
    with open("tests/data/concat.txt", "r") as f:
        return f.readlines()


@pytest.fixture
def fake_streams():
    with open("tests/data/streams_pickle", "rb") as f:
        return pickle.load(f)


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


@pytest.fixture
def fake_retry_content():
    with open("tests/data/fake_retry", "r") as f:
        return f.readlines()
