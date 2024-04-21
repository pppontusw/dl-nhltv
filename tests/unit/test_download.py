from datetime import datetime
import pytest
from nhltv_lib.download import (
    _verify_nhltv_request_status_succeeded,
    _extract_session_key,
    _get_raw_file_name,
    _create_download_folder,
)
from nhltv_lib.exceptions import (
    BlackoutRestriction,
    AuthenticationFailed,
)
from nhltv_lib.models import GameStatus

FAKE_URL = "http://nhl"


@pytest.fixture(scope="function")
def mock_datetime(mocker):
    da = datetime.now()
    mocktime = mocker.patch("nhltv_lib.download.datetime")
    mocktime.now.return_value = da
    return da


@pytest.fixture(scope="function", autouse=True)
def mock_game_tracking(mocker):
    return mocker.patch("nhltv_lib.download.game_tracking")


@pytest.fixture(scope="function", autouse=True)
def mock_rmtree(mocker):
    return mocker.patch("nhltv_lib.download.rmtree")


def test_get_raw_file_name():
    assert _get_raw_file_name(30) == "30_raw.mkv"


def test_extract_session_key(mocker):
    retjson = {"data": 3000}
    assert _extract_session_key(retjson) == "3000"


def test_verify_req_stat_succeeded():
    dict_ = {"status": "success"}
    assert _verify_nhltv_request_status_succeeded(dict_) is None


def test_verify_req_stat_succeeded_raises():
    dict_ = {"status": "failed"}
    with pytest.raises(AuthenticationFailed):
        _verify_nhltv_request_status_succeeded(dict_)


def test_create_dl_folder(mocker, mock_os_path_exists):
    mock_os_path_exists.return_value = False
    mock_mkdirs = mocker.patch("os.makedirs")
    _create_download_folder(1)
    mock_mkdirs.assert_called_once_with("1")
