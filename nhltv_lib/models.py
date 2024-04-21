from enum import Enum as PythonEnum

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


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


# pylint: disable=too-few-public-methods
class DbGame(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    home_team = Column(String(250))
    away_team = Column(String(250))
    time = Column(DateTime)
    status = Column(Enum(GameStatus), nullable=False)
    current_operation_progress = Column(Integer)
    game_info = Column(String(250))
    download_attempts = Column(Integer)
    download_start = Column(DateTime)
    download_end = Column(DateTime)
    next_attempt = Column(DateTime)
