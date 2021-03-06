from typing import Dict, Iterable, Tuple
from datetime import datetime, timedelta
from nhltv_lib.json_repository import read_json_dict, add_to_json_dict


def get_blackout_wait_list() -> Dict[str, str]:
    return dict(filter_out_old_entries(read_json_dict("blackout_waitlist")))


def filter_out_old_entries(
    waitlist: Dict[str, str]
) -> Iterable[Tuple[str, str]]:
    return filter(
        lambda x: datetime.fromisoformat(x[1]) > datetime.now(),
        waitlist.items(),
    )


def add_game_to_blackout_wait_list(game_id: int) -> None:
    game_to_add = {
        str(game_id): (datetime.now() + timedelta(hours=4)).isoformat()
    }
    add_to_json_dict("blackout_waitlist", game_to_add)
