import os
from collections import namedtuple
import pytest


@pytest.fixture
def ParsedArgs():
    return namedtuple(
        "ParsedArgs",
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
        "username",
        "password",
        "3333",
        os.getcwd() + "/test",
        "10",
        "4",
        "2",
        True,
        False,
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
        "--download_folder",
        os.getcwd() + "/test",
        "--keep",
        "5",
        "--obfuscate",
    ]


@pytest.fixture(scope="function", autouse=True)
def mocked_logger(mocker):
    with mocker.patch("logging.getLogger"):
        yield
