# flake8: noqa
import pickle
import os
import json
from collections import namedtuple
import pytest
from nhltv_lib.game import Game


@pytest.fixture
def ParsedArgs():
    return namedtuple(
        "Arguments",
        [
            "username",
            "password",
            "quality",
            "download_folder",
            "checkinterval",
            "retentiondays",
            "days_back_to_search",
            "obfuscate",
            "shorten_video",
            "debug_dumps_enabled",
        ],
    )


@pytest.fixture
def parsed_args_list():
    return [
        "username",  # 0
        "password",  # 1
        "3333",  # 2 quality
        os.getcwd() + "/test",  # 3 dl folder
        "10",  # 4 checkinterval
        "4",  # 5 days to keep
        "2",  # 6 days back to search
        True,  # 7 obfuscate
        False,  # 8 shorten video
        False,  # 9 debug dumps
    ]


@pytest.fixture
def parsed_arguments(ParsedArgs, parsed_args_list):
    return ParsedArgs(*parsed_args_list)


@pytest.fixture
def arguments_list():
    return [
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
        "--obfuscate",
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
    with mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    ):
        yield


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
