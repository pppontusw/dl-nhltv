from datetime import datetime
import pytest
from nhltv_lib.common import (
    write_lines_to_file,
    read_lines_from_file,
    move_file_to_download_folder,
    dump_json_if_debug_enabled,
    dump_pickle_if_debug_enabled,
    debug_dump_json,
    debug_dump_pickle,
)


@pytest.fixture(scope="function")
def mock_datetime(mocker):
    da = datetime.now()
    mocktime = mocker.patch("nhltv_lib.common.datetime")
    mocktime.now.return_value = da
    return da


def test_write_lines_to_file(mocker):
    call = mocker.call
    mo = mocker.mock_open()
    mocker.patch("builtins.open", mo)
    write_lines_to_file(["foo", "bar"], "file")
    mo.assert_called_with("file", "w")
    calls = [call(["foo", "bar"])]
    mo().writelines.assert_has_calls(calls)


def test_read_lines_from_file(mocker):
    mo = mocker.mock_open(read_data="coo\nloo")
    mocker.patch("builtins.open", mo)
    assert read_lines_from_file(1) == ["coo\n", "loo"]


def test_move_file_to_download_folder(mocker, fake_download):
    mocker.patch("nhltv_lib.common.get_download_folder", return_value="./foo")
    mocker.patch("pathlib.Path.mkdir")
    mv = mocker.patch("nhltv_lib.common.move")
    move_file_to_download_folder(fake_download)
    mv.assert_called_once_with(
        f"{fake_download.game_id}_ready.mkv",
        f"./foo/{fake_download.game_info}.mkv",
    )


def test_dump_json_if_debug(mocker):
    mj = mocker.patch("nhltv_lib.common.debug_dump_json")
    mocker.patch("nhltv_lib.common.debug_dumps_enabled", return_value=True)
    dump_json_if_debug_enabled({"foo": "bar"})
    mj.assert_called_once_with(
        {"foo": "bar"}, caller="test_dump_json_if_debug"
    )


def test_dump_json_if_not_debug(mocker):
    mj = mocker.patch("nhltv_lib.common.debug_dump_json")
    mocker.patch("nhltv_lib.common.debug_dumps_enabled", return_value=False)
    dump_json_if_debug_enabled({"foo": "bar"})
    assert not mj.called


def test_dump_pickle_if_not_debug(mocker):
    mj = mocker.patch("nhltv_lib.common.debug_dump_pickle")
    mocker.patch("nhltv_lib.common.debug_dumps_enabled", return_value=False)
    dump_pickle_if_debug_enabled({"foo": "bar"})
    assert not mj.called


def test_dump_pickle_if_debug(mocker):
    mj = mocker.patch("nhltv_lib.common.debug_dump_pickle")
    mocker.patch("nhltv_lib.common.debug_dumps_enabled", return_value=True)
    dump_pickle_if_debug_enabled({"foo": "bar"})
    mj.assert_called_once_with(
        {"foo": "bar"}, caller="test_dump_pickle_if_debug"
    )


def test_dump_json(mocker, mock_datetime):
    mj = mocker.patch("json.dump")
    mo = mocker.mock_open()
    mocker.patch("nhltv_lib.common.open", mo)
    debug_dump_json({"foo": "bar"})
    mo.assert_called_once_with(f"_{mock_datetime.isoformat()}.json", "w")
    mj.assert_called_once_with({"foo": "bar"}, mo())


def test_dump_json_w_caller(mocker, mock_datetime):
    mj = mocker.patch("json.dump")
    mo = mocker.mock_open()
    mocker.patch("nhltv_lib.common.open", mo)
    debug_dump_json({"foo": "bar"}, caller="baz")
    mo.assert_called_once_with(f"baz_{mock_datetime.isoformat()}.json", "w")
    mj.assert_called_once_with({"foo": "bar"}, mo())


def test_dump_pickle(mocker, mock_datetime):
    mj = mocker.patch("pickle.dump")
    mo = mocker.mock_open()
    mocker.patch("nhltv_lib.common.open", mo)
    debug_dump_pickle({"foo": "bar"})
    mo.assert_called_once_with(f"_{mock_datetime.isoformat()}.pickle", "wb")
    mj.assert_called_once_with({"foo": "bar"}, mo())


def test_dump_pickle_w_caller(mocker, mock_datetime):
    mj = mocker.patch("pickle.dump")
    mo = mocker.mock_open()
    mocker.patch("nhltv_lib.common.open", mo)
    debug_dump_pickle({"foo": "bar"}, caller="boo")
    mo.assert_called_once_with(f"boo_{mock_datetime.isoformat()}.pickle", "wb")
    mj.assert_called_once_with({"foo": "bar"}, mo())
