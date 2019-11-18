from datetime import datetime, timedelta
from nhltv_lib.json_repository import read_json_dict, add_to_json_dict


def get_archive_wait_list():
    return dict(filter_out_old_entries(read_json_dict("archive_waitlist")))


def get_blackout_wait_list():
    return dict(filter_out_old_entries(read_json_dict("blackout_waitlist")))


def filter_out_old_entries(waitlist):
    return filter(
        lambda x: datetime.fromisoformat(x[1]) > datetime.now(),
        waitlist.items(),
    )


def add_game_to_archive_wait_list(game_id):
    game_to_add = {
        str(game_id): (datetime.now() + timedelta(minutes=15)).isoformat()
    }
    add_to_json_dict("archive_waitlist", game_to_add)


def add_game_to_blackout_wait_list(game_id):
    game_to_add = {
        str(game_id): (datetime.now() + timedelta(hours=4)).isoformat()
    }
    add_to_json_dict("blackout_waitlist", game_to_add)
