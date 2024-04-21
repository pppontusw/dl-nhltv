from typing import Union
from nhltv_lib.common import dump_json_if_debug_enabled
from nhltv_lib.constants import HEADERS
import nhltv_lib.requests_wrapper as requests
from nhltv_lib.urls import TEAMS_URL


def get_team(search: Union[int, str]) -> int:
    """
    search (int | str):
        int: team id number like 17
        STR: abbreviation like "DET"
        str: team name like "Detroit Red Wings"

    Returns:
       int: team id
    """

    if isinstance(search, int):
        return find_team_by_id(search)

    if search.isupper():
        return find_team_by_abbreviation(search)

    return find_team_by_name(search)


def fetch_teams() -> dict:
    teams = requests.get(TEAMS_URL, headers={**HEADERS}).json()
    dump_json_if_debug_enabled(teams)
    return teams


def find_team_by_id(team_id: int) -> int:
    team_json = fetch_teams()
    return list(filter(lambda x: x["id"] == team_id, team_json["data"]))[0][
        "id"
    ]


def find_team_by_abbreviation(abbreviation: str) -> int:
    team_json = fetch_teams()
    return list(
        filter(lambda x: x["triCode"] == abbreviation, team_json["data"])
    )[0]["id"]


def find_team_by_name(name: str) -> int:
    team_json = fetch_teams()
    return list(filter(lambda x: x["commonName"] == name, team_json["data"]))[
        0
    ]["id"]
