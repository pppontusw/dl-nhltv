from datetime import datetime
import pytest
from nhltv_lib.common import (
    write_lines_to_file,
    touch,
    read_lines_from_file,
    move_file_to_download_folder,
    dump_json_if_debug_enabled,
    dump_pickle_if_debug_enabled,
    debug_dump_json,
    debug_dump_pickle,
    tprint,
    debug_dumps_enabled,
    print_progress_bar,
)


@pytest.fixture(scope="function")
def mock_datetime(mocker):
    da = datetime.now()
    mocktime = mocker.patch("nhltv_lib.common.datetime")
    mocktime.now.return_value = da
    return da


@pytest.fixture(scope="function")
def mock_isfile(mocker):
    return mocker.patch("nhltv_lib.common.os.path.isfile")


@pytest.fixture(scope="function")
def mock_isdir(mocker):
    return mocker.patch("nhltv_lib.common.os.path.isdir")


@pytest.fixture(scope="function")
def mock_path_touch(mocker):
    return mocker.patch("nhltv_lib.common.Path.touch")


def test_touch(mock_isfile, mock_path_touch):
    mock_isfile.return_value = True
    touch("boo")
    mock_path_touch.assert_not_called()


def test_touch_yes(mock_isfile, mock_path_touch):
    mock_isfile.return_value = False
    touch("boo")
    mock_path_touch.assert_called_once()


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


def test_debug_dumps_enabled(
    mocker, mock_isdir, parsed_args, parsed_args_list
):
    mock_isdir.return_value = False
    parsed_args_list[9] = True
    mocker.patch(
        "nhltv_lib.common.get_arguments",
        return_value=parsed_args(*parsed_args_list),
    )
    mkdir = mocker.patch("nhltv_lib.common.os.mkdir")
    debug_dumps_enabled()
    mkdir.assert_called_once_with("dumps")


@pytest.fixture
def mock_debug_dumps_enabled(mocker):
    return mocker.patch(
        "nhltv_lib.common.debug_dumps_enabled", return_value=True
    )


@pytest.fixture
def mock_print(mocker):
    return mocker.patch("nhltv_lib.common.print")


def test_dump_json_if_debug(mocker, mock_debug_dumps_enabled):
    mj = mocker.patch("nhltv_lib.common.debug_dump_json")
    dump_json_if_debug_enabled({"foo": "bar"})
    mj.assert_called_once_with(
        {"foo": "bar"}, caller="test_dump_json_if_debug"
    )


def test_dump_json_if_not_debug(mocker, mock_debug_dumps_enabled):
    mj = mocker.patch("nhltv_lib.common.debug_dump_json")
    mock_debug_dumps_enabled.return_value = False
    dump_json_if_debug_enabled({"foo": "bar"})
    assert not mj.called


def test_dump_pickle_if_not_debug(mocker, mock_debug_dumps_enabled):
    mj = mocker.patch("nhltv_lib.common.debug_dump_pickle")
    mock_debug_dumps_enabled.return_value = False
    dump_pickle_if_debug_enabled({"foo": "bar"})
    assert not mj.called


def test_dump_pickle_if_debug(mocker, mock_debug_dumps_enabled):
    mj = mocker.patch("nhltv_lib.common.debug_dump_pickle")
    dump_pickle_if_debug_enabled({"foo": "bar"})
    mj.assert_called_once_with(
        {"foo": "bar"}, caller="test_dump_pickle_if_debug"
    )


@pytest.fixture
def mock_open(mocker):
    mock_open = mocker.mock_open()
    mocker.patch("nhltv_lib.common.open", mock_open)
    return mock_open


def test_dump_json(mocker, mock_datetime, mock_open):
    mj = mocker.patch("json.dump")
    debug_dump_json({"foo": "bar"})
    mock_open.assert_called_once_with(
        f"dumps/_{mock_datetime.isoformat()}.json", "w"
    )
    mj.assert_called_once_with({"foo": "bar"}, mock_open())


def test_dump_json_w_caller(mocker, mock_datetime, mock_open):
    mj = mocker.patch("json.dump")
    debug_dump_json({"foo": "bar"}, caller="baz")
    mock_open.assert_called_once_with(
        f"dumps/baz_{mock_datetime.isoformat()}.json", "w"
    )
    mj.assert_called_once_with({"foo": "bar"}, mock_open())


def test_dump_pickle(mocker, mock_datetime, mock_open):
    mj = mocker.patch("pickle.dump")
    debug_dump_pickle({"foo": "bar"})
    mock_open.assert_called_once_with(
        f"dumps/_{mock_datetime.isoformat()}.pickle", "wb"
    )
    mj.assert_called_once_with({"foo": "bar"}, mock_open())


def test_dump_pickle_w_caller(mocker, mock_datetime, mock_open):
    mj = mocker.patch("pickle.dump")
    debug_dump_pickle({"foo": "bar"}, caller="boo")
    mock_open.assert_called_once_with(
        f"dumps/boo_{mock_datetime.isoformat()}.pickle", "wb"
    )
    mj.assert_called_once_with({"foo": "bar"}, mock_open())


def test_tprint(mocker, mock_datetime):
    mp = mocker.patch("builtins.print")
    tprint("boo")
    mp.assert_called_once_with(
        f"{mock_datetime.strftime('%b %-d %H:%M:%S')} - boo"
    )


def test_tprint_debug_off(
    mocker, mock_datetime, mock_debug_dumps_enabled, mock_print
):
    mock_debug_dumps_enabled.return_value = False
    tprint("boo", True)
    mock_print.assert_not_called()


def test_tprint_debug_on(
    mocker, mock_datetime, mock_debug_dumps_enabled, mock_print
):
    mock_debug_dumps_enabled.return_value = True
    tprint("boo", True)
    mock_print.assert_called_once_with(
        f"{mock_datetime.strftime('%b %-d %H:%M:%S')} - boo"
    )


def test_progress_bar(mocker, mock_print):
    print_progress_bar(1, 2, "p", "s", 1, 2, "X")
    print_progress_bar(2, 2, "p", "s", 1, 2, "X")
    call = mocker.call
    mock_print.assert_has_calls(
        [
            call("\rp |X-| 50.0% s", end="\r"),
            call("\rp |XX| 100.0% s", end="\r"),
            call(),
        ]
    )
