# pylint: disable=too-few-public-methods
import datetime
from enum import Enum as PythonEnum
from typing import Optional

from sqlalchemy import Integer, String, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class GameStatus(PythonEnum):
    blackout = "Blacked Out"
    auth_failure = "Authentication Failed (retrying..)"
    waiting = "Waiting to download"
    downloading = "Downloading"
    decoding = "Decoding video"
    skip_silence = "Removing commercial breaks"
    obfuscating = "Obfuscating video end"
    moving = "Moving to final destination"
    completed = "Completed"


class DbGame(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    home_team: Mapped[Optional[str]] = mapped_column(String(250))
    away_team: Mapped[Optional[str]] = mapped_column(String(250))
    time: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    status: Mapped[GameStatus] = mapped_column(
        SQLAlchemyEnum(GameStatus), nullable=False
    )
    current_operation_progress: Mapped[Optional[int]] = mapped_column(Integer)
    game_info: Mapped[Optional[str]] = mapped_column(String(250))
    download_attempts: Mapped[Optional[int]] = mapped_column(Integer)
    download_start: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )
    download_end: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    next_attempt: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
