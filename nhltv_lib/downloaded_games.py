from typing import List
from nhltv_lib.json_repository import read_json_list, add_to_json_list


def get_downloaded_games() -> List[int]:
    return [
        i for i in read_json_list("downloaded_games") if isinstance(i, int)
    ]


def add_to_downloaded_games(game_id: int) -> None:
    add_to_json_list("downloaded_games", game_id)
