from datetime import datetime, timedelta
import pytest
from nhltv_lib.game_tracking import (
    start_tracking_game,
    _get_game_from_db,
    set_game_info,
    update_progress,
    update_game_status,
    clear_progress,
    get_download_attempts,
    set_download_attempts,
    increment_download_attempts,
    download_started,
    download_finished,
    game_not_downloaded,
    ready_for_next_attempt,
    set_blackout,
)
from nhltv_lib.models import DbGame, GameStatus


@pytest.fixture(scope="function", autouse=True)
def mock_game(mock_db_session):
    game = DbGame(id=80, status=GameStatus.completed)
    mock_db_session.add(game)
    mock_db_session.commit()
    return game


def test_get_game_from_db(mock_db_session, mock_game):
    assert _get_game_from_db(80) == mock_game


def test_start_tracking_game(mock_db_session):
    t = datetime.now()
    start_tracking_game(1, t, "foo", "bar")

    assert mock_db_session.query(DbGame).first().id == 1
    assert mock_db_session.query(DbGame).first().time == t
    assert mock_db_session.query(DbGame).first().home_team == "foo"
    assert mock_db_session.query(DbGame).first().away_team == "bar"


def test_set_game_info(mock_db_session, mock_game):
    set_game_info(mock_game.id, "foobar")
    assert mock_game.game_info == "foobar"


def test_update_game_status(mock_db_session, mock_game):
    update_game_status(mock_game.id, GameStatus.decoding)
    assert mock_game.status == GameStatus.decoding


def test_update_progress(mock_db_session, mock_game):
    update_progress(mock_game.id, 80, 100)
    assert mock_game.current_operation_progress == 80

    update_progress(mock_game.id, 6, 10)
    assert mock_game.current_operation_progress == 60


def test_clear_progress(mock_db_session, mock_game):
    mock_game.progress = 80
    clear_progress(mock_game.id)
    assert mock_game.current_operation_progress is None


def test_get_download_attempts(mock_db_session, mock_game):
    mock_game.download_attempts = 80
    assert get_download_attempts(mock_game.id) == 80


def test_set_download_attempts(mock_db_session, mock_game):
    mock_game.download_attempts = 80
    set_download_attempts(mock_game.id, 1)
    assert mock_game.download_attempts == 1


def test_increment_download_attempts(mock_db_session, mock_game):
    mock_game.download_attempts = 80
    increment_download_attempts(mock_game.id)
    assert mock_game.download_attempts == 81


def test_increment_download_attempts_uninitialized(mock_db_session, mock_game):
    mock_game.download_attempts = None
    increment_download_attempts(mock_game.id)
    assert mock_game.download_attempts == 1


@pytest.fixture(scope="function")
def mock_datetime(mocker):
    da = datetime.now()
    mocktime = mocker.patch("nhltv_lib.game_tracking.datetime")
    mocktime.now.return_value = da
    return da


def test_dl_started(mock_db_session, mock_game, mock_datetime):
    download_started(mock_game.id)
    assert mock_game.download_start == mock_datetime


def test_dl_finished(mock_db_session, mock_game, mock_datetime):
    download_finished(mock_game.id)
    assert mock_game.download_end == mock_datetime


def test_game_not_downloaded(mock_db_session, mock_game):
    mock_game.status = GameStatus.completed
    assert not game_not_downloaded(mock_game.id)


def test_game_not_downloaded_yes(mock_db_session, mock_game):
    mock_game.status = GameStatus.downloading
    assert game_not_downloaded(mock_game.id)


def test_set_blackout(mock_db_session, mock_game, mock_datetime):
    set_blackout(mock_game.id)
    assert mock_game.status == GameStatus.blackout
    assert mock_game.next_attempt == mock_datetime + timedelta(hours=4)


def test_ready_for_next_attempt(mock_db_session, mock_game):
    mock_game.next_attempt = datetime.now() - timedelta(hours=4)
    assert ready_for_next_attempt(mock_game.id)


def test_ready_for_next_attempt_empty(mock_db_session, mock_game):
    mock_game.next_attempt = None
    assert ready_for_next_attempt(mock_game.id)


def test_ready_for_next_attempt_not(mock_db_session, mock_game):
    mock_game.next_attempt = datetime.now() + timedelta(hours=4)
    assert not ready_for_next_attempt(mock_game.id)
