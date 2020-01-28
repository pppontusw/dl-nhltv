import pytest
from nhltv_lib.exceptions import AuthenticationFailed, BlackoutRestriction
from nhltv_lib.main import (
    verify_dependencies,
    get_and_download_games,
    download,
    loop,
)


@pytest.fixture(scope="function", autouse=True)
def mock_game_tracking(mocker):
    return mocker.patch("nhltv_lib.main.game_tracking")


@pytest.fixture(scope="function", autouse=True)
def mock_login(mocker):
    return mocker.patch("nhltv_lib.main.login_and_save_cookie")


@pytest.fixture(scope="function", autouse=True)
def mock_run_loop(mocker):
    return mocker.patch("nhltv_lib.main.run_loop")


@pytest.fixture(scope="function", autouse=True)
def mock_get_games(mocker):
    return mocker.patch("nhltv_lib.main.get_games_to_download")


@pytest.fixture(scope="function", autouse=True)
def mock_download_game(mocker, fake_download):
    return mocker.patch(
        "nhltv_lib.main.download_game", return_value=fake_download
    )


@pytest.fixture(scope="function", autouse=True)
def mock_skip_silence(mocker):
    return mocker.patch("nhltv_lib.main.skip_silence")


@pytest.fixture(scope="function", autouse=True)
def mock_obfuscate(mocker):
    return mocker.patch("nhltv_lib.main.obfuscate")


@pytest.fixture(scope="function", autouse=True)
def mock_clean_up_download(mocker):
    return mocker.patch("nhltv_lib.main.clean_up_download")


@pytest.fixture(scope="function", autouse=True)
def mock_add_game_to_blkout(mock_game_tracking):
    return mock_game_tracking.set_blackout


@pytest.fixture(scope="function", autouse=True)
def mock_add_to_downloaded_games(mocker):
    return mocker.patch("nhltv_lib.main.add_to_downloaded_games")


@pytest.fixture(scope="function", autouse=True)
def mock_sleep(mocker):
    return mocker.patch("nhltv_lib.main.sleep")


@pytest.fixture(scope="function", autouse=True)
def mock_get_and_dl_games(mocker):
    return mocker.patch("nhltv_lib.main.get_and_download_games")


@pytest.fixture(scope="function", autouse=True)
def mock_get_checkinterval(mocker):
    return mocker.patch("nhltv_lib.main.get_checkinterval", return_value=10)


@pytest.fixture(scope="function", autouse=True)
def mock_get_auth_cookie_expires(mocker):
    return mocker.patch(
        "nhltv_lib.main.get_auth_cookie_expires_in_minutes", return_value=60
    )


def test_loop(
    mock_get_and_dl_games,
    mock_sleep,
    mock_get_checkinterval,
    mock_get_auth_cookie_expires,
    mock_login,
):
    loop()
    mock_get_and_dl_games.assert_called_once()
    mock_get_checkinterval.assert_called_once()
    mock_sleep.assert_called_once_with(600)
    mock_get_auth_cookie_expires.assert_called_once()
    assert mock_login.call_count == 0


def test_loop_sleep_by_checkinterval(mock_sleep, mock_get_checkinterval):
    mock_get_checkinterval.return_value = 60
    loop()
    mock_sleep.assert_called_once_with(60 * 60)


def test_loop_login_required_none(mock_get_auth_cookie_expires, mock_login):
    mock_get_auth_cookie_expires.return_value = None
    loop()
    mock_login.assert_called_once()


def test_loop_login_required_sub_30(mock_get_auth_cookie_expires, mock_login):
    mock_get_auth_cookie_expires.return_value = 28
    loop()
    mock_login.assert_called_once()


def test_verify_deps(mocker):
    mock_verify_deps = mocker.patch("nhltv_lib.main.verify_cmd_exists_in_path")
    verify_dependencies()
    mock_verify_deps.assert_called()


def test_get_and_download_games(
    mocker, mock_get_games, fake_games, fake_streams
):
    call = mocker.call
    mock_get_games.return_value = fake_games[:2]

    mock_get_streams = mocker.patch(
        "nhltv_lib.main.get_streams_to_download", return_value=fake_streams[:2]
    )
    mock_dl = mocker.patch("nhltv_lib.main.download")

    get_and_download_games()

    mock_get_games.assert_called_once()
    mock_get_streams.assert_called_once_with(fake_games[:2])
    calls = [call(fake_streams[0]), call(fake_streams[1])]
    mock_dl.assert_has_calls(calls)


def test_download(
    mock_download_game,
    mock_skip_silence,
    mock_obfuscate,
    mock_add_to_downloaded_games,
    mock_clean_up_download,
    fake_download,
    fake_streams,
):
    download(fake_streams[0])
    mock_download_game.assert_called_once_with(fake_streams[0])
    mock_skip_silence.assert_called_once_with(fake_download)
    mock_obfuscate.assert_called_once_with(fake_download)
    mock_clean_up_download.assert_called_once_with(
        fake_download.game_id, delete_cookie=True
    )
    mock_add_to_downloaded_games.assert_called_once_with(fake_download.game_id)


def test_download_throws_authenticationfailed(
    mocker, mock_sleep, mock_download_game, fake_streams, fake_download
):
    mock_download_game.side_effect = [AuthenticationFailed, fake_download]
    download(fake_streams[0])
    mock_sleep.assert_called_once()
    assert mock_download_game.call_count == 2


def test_download_throws_blackoutrestriction(
    mock_download_game, fake_streams, mock_add_game_to_blkout
):
    mock_download_game.side_effect = BlackoutRestriction
    download(fake_streams[0])
    mock_add_game_to_blkout.assert_called_once_with(fake_streams[0].game_id)
