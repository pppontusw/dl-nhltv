import json
from nhltv_lib.json_repository import (
    read_json_list,
    ensure_json_list_exists,
    read_json_dict,
    ensure_json_dict_exists,
    add_to_json_dict,
)


def test_ensure_json_list_exists(mocker):
    mocker.patch("os.path.exists", return_value=False)
    m_open = mocker.mock_open()
    mocker.patch("nhltv_lib.json_repository.open", m_open)
    ensure_json_list_exists("test")
    handle = m_open()
    handle.write.assert_called_once_with(json.dumps(list()))


def test_read_json_list(mocker):
    mocker.patch("nhltv_lib.json_repository.ensure_json_list_exists")
    m_open = mocker.mock_open(read_data="[392]")
    mocker.patch("nhltv_lib.json_repository.open", m_open)
    assert read_json_list("test") == [392]


def test_ensure_json_dict_exists(mocker):
    mocker.patch("os.path.exists", return_value=False)
    m_open = mocker.mock_open()
    mocker.patch("nhltv_lib.json_repository.open", m_open)
    ensure_json_dict_exists("test")
    handle = m_open()
    handle.write.assert_called_once_with(json.dumps(dict()))


def test_read_json_dict(mocker):
    mocker.patch("nhltv_lib.json_repository.ensure_json_dict_exists")
    m_open = mocker.mock_open(read_data='{"392": "booboo"}')
    mocker.patch("nhltv_lib.json_repository.open", m_open)
    assert read_json_dict("test") == {"392": "booboo"}


def test_add_to_json_dict(mocker):
    call = mocker.call
    mocker.patch("nhltv_lib.json_repository.ensure_json_dict_exists")
    m_open = mocker.mock_open(read_data='{"392": "booboo"}')
    mocker.patch("nhltv_lib.json_repository.open", m_open)
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
    m_open().write.assert_has_calls(calls)


def test_add_to_json_dict_empty(mocker):
    call = mocker.call
    mocker.patch("nhltv_lib.json_repository.ensure_json_dict_exists")
    m_open = mocker.mock_open(read_data="{}")
    mocker.patch("nhltv_lib.json_repository.open", m_open)
    add_to_json_dict("test", {"2000": "3000"})
    calls = [call("{"), call('"2000"'), call(": "), call('"3000"'), call("}")]
    m_open().write.assert_has_calls(calls)
