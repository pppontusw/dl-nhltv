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
        ],
    )


@pytest.fixture
# pylint: disable=redefined-outer-name
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
    ]


@pytest.fixture
# pylint: disable=redefined-outer-name
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
# pylint: disable=redefined-outer-name
def mocked_fetch_teams(mocker, teams_data):
    return mocker.patch("nhltv_lib.teams.fetch_teams", return_value=teams_data)


@pytest.fixture
def games_data():
    with open("tests/data/games.json", "r") as f:
        return json.load(f)


@pytest.fixture(scope="function", autouse=True)
# pylint: disable=redefined-outer-name
def mocked_fetch_games(mocker, games_data):
    return mocker.patch("nhltv_lib.game.fetch_games", return_value=games_data)


@pytest.fixture(scope="function", autouse=True)
# pylint:disable=redefined-outer-name
def mocked_parse_args(mocker, parsed_arguments):
    with mocker.patch(
        # pylint:disable=bad-continuation
        "nhltv_lib.arguments.parse_args",
        return_value=parsed_arguments,
    ):
        yield


@pytest.fixture
# pylint:disable=redefined-outer-name
def fake_game_objects(games_data):
    games = games_data["dates"][0]["games"]
    return tuple(
        Game(i["gamePk"], True, i["content"]["media"]["epg"][0]["items"])
        for i in games
    )
