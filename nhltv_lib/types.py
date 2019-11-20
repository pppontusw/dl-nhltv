from collections import namedtuple
from typing import TypeVar

Stream = namedtuple("Stream", ["game_id", "content_id", "event_id"])

Game = namedtuple("Game", ["game_id", "is_home_game", "streams"])

GameDict = TypeVar("GameDict", bound=dict)

Download = namedtuple(
    "Download", ["game_id", "game_info", "stream_url", "session_key"]
)

NHLTVUser = namedtuple("NHLTVUser", ["username", "password"])
