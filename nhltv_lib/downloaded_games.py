from nhltv_lib.json_repository import read_json_list, add_to_json_list


def get_downloaded_games():
    return read_json_list("downloaded_games")


def add_to_downloaded_games(game_id):
    add_to_json_list("downloaded_games", game_id)
