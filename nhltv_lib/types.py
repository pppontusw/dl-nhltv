from collections import namedtuple
from typing import TypeVar

NHLStream = namedtuple("NHLStream", ["game_id", "stream", "player_settings"])

Game = namedtuple("Game", ["game_id", "is_home_game", "streams"])

GameDict = TypeVar("GameDict", bound=dict)

Download = namedtuple(
    "Download", ["game_id", "game_info", "stream_url", "session_key"]
)

NHLTVUser = namedtuple("NHLTVUser", ["username", "password"])
