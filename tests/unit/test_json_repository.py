import json
import pytest
from nhltv_lib.json_repository import (
    read_json_list,
    ensure_json_list_exists,
    read_json_dict,
    ensure_json_dict_exists,
    add_to_json_dict,
    add_to_json_list,
)


def mock_json_open(mocker, m_open):
    return mocker.patch("nhltv_lib.json_repository.open", m_open)


@pytest.fixture
def m_open(mocker):
    m_open = mocker.mock_open(read_data="[392]")
    mock_json_open(mocker, m_open)
    return m_open


@pytest.fixture
def m_open_dict(mocker):
    m_open = mocker.mock_open(read_data='{"392": "booboo"}')
    mock_json_open(mocker, m_open)
    return m_open


@pytest.fixture(autouse=True)
def mock_json_list_exists(mocker):
    return mocker.patch("nhltv_lib.json_repository.ensure_json_list_exists")


@pytest.fixture(autouse=True)
def mock_json_dict_exists(mocker):
    return mocker.patch("nhltv_lib.json_repository.ensure_json_dict_exists")


@pytest.fixture(autouse=True)
def mock_os_path_exists(mocker):
    return mocker.patch("os.path.exists", return_value=False)


def test_ensure_json_list_exists(mocker, m_open):
    ensure_json_list_exists("test")
    handle = m_open()
    handle.write.assert_called_once_with(json.dumps(list()))


def test_read_json_list(mocker, m_open):
    assert read_json_list("test") == [392]


def test_ensure_json_dict_exists(mocker, m_open):
    ensure_json_dict_exists("test")
    handle = m_open()
    handle.write.assert_called_once_with(json.dumps(dict()))


def test_add_to_json_list(mocker, m_open):
    mocker.patch(
        "nhltv_lib.json_repository.read_json_list", return_value=[392, "boooo"]
    )
    mjson = mocker.patch("json.dump")
    add_to_json_list("test", 2000)
    mjson.assert_called_once_with([392, "boooo", 2000], m_open())


def test_read_json_dict(mocker, m_open_dict):
    assert read_json_dict("test") == {"392": "booboo"}


def test_add_to_json_dict(mocker, m_open_dict):
    call = mocker.call
    add_to_json_dict("test", {"2000": "3000"})
    calls = [
        call("{"),
        call('"392"'),
        call(": "),
        call('"booboo"'),
        call(", "),
        call('"2000"'),
        call(": "),
        call('"3000"'),
        call("}"),
    ]
    m_open_dict().write.assert_has_calls(calls)


def test_add_to_json_dict_empty(mocker):
    call = mocker.call
    m_open = mocker.mock_open(read_data="{}")
    mock_json_open(mocker, m_open)
    add_to_json_dict("test", {"2000": "3000"})
    calls = [call("{"), call('"2000"'), call(": "), call('"3000"'), call("}")]
    m_open().write.assert_has_calls(calls)
