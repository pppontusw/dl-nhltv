from typing import Optional
from datetime import datetime, timedelta
from nhltv_lib.models import DbGame, GameStatus
import nhltv_lib.db_session as db


def _get_game_from_db(game_id: int) -> DbGame:
    return db.session.query(DbGame).filter(DbGame.id == game_id).first()


def start_tracking_game(
    game_id: int,
    time: datetime,
    home_team: str,
    away_team: str,
    status: GameStatus = GameStatus.waiting,
) -> DbGame:
    game = _get_game_from_db(game_id)
    if not game:
        game = DbGame(  # type: ignore
            id=game_id,
            time=time,
            status=status,
            home_team=home_team,
            away_team=away_team,
        )
        db.session.add(game)
        db.session.commit()
    return game


def set_game_info(game_id: int, game_info: str) -> None:
    game = _get_game_from_db(game_id)
    game.game_info = game_info
    db.session.commit()


def update_game_status(game_id: int, status: GameStatus) -> None:
    game = _get_game_from_db(game_id)
    game.status = status  # type: ignore
    db.session.commit()


def update_progress(game_id: int, progress: int, total: int) -> None:
    game = _get_game_from_db(game_id)
    game.current_operation_progress = int((progress / total) * 100)
    db.session.commit()


def clear_progress(game_id: int) -> None:
    game = _get_game_from_db(game_id)
    game.current_operation_progress = None
    db.session.commit()


def get_download_attempts(game_id: int) -> Optional[int]:
    return _get_game_from_db(game_id).download_attempts


def set_download_attempts(game_id: int, attempts: int) -> None:
    game = _get_game_from_db(game_id)
    game.download_attempts = attempts
    db.session.commit()


def increment_download_attempts(game_id: int) -> None:
    game = _get_game_from_db(game_id)
    if game.download_attempts:
        game.download_attempts += 1
    else:
        game.download_attempts = 1
    db.session.commit()


def download_started(game_id: int) -> None:
    game = _get_game_from_db(game_id)
    game.download_start = datetime.now()
    db.session.commit()


def download_finished(game_id: int) -> None:
    game = _get_game_from_db(game_id)
    game.download_end = datetime.now()
    db.session.commit()


def game_not_downloaded(game_id: int) -> bool:
    game = _get_game_from_db(game_id)
    if not game:
        return True
    return game.status != GameStatus.completed


def ready_for_next_attempt(game_id: int) -> bool:
    game = _get_game_from_db(game_id)
    if not game or not game.next_attempt:
        return True
    return game.next_attempt <= datetime.now()


def set_blackout(game_id: int) -> None:
    update_game_status(game_id, GameStatus.blackout)
    game = _get_game_from_db(game_id)
    game.next_attempt = datetime.now() + timedelta(hours=4)
