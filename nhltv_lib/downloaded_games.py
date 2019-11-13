from nhltv_lib.json_repository import read_json_list


def get_downloaded_games():
    return read_json_list("downloaded_games")
