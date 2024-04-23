from typing import Union
from nhltv_lib.cache import cache_json, load_cache_json
from nhltv_lib.common import dump_json_if_debug_enabled, verify_request_200
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
    # Try to load the data from cache first
    cached_teams = load_cache_json("teams", {})
    if cached_teams is not None:
        return cached_teams

    # If not cached or cache is expired, fetch from the API
    response = requests.get(TEAMS_URL, headers=HEADERS, timeout=15)
    verify_request_200(response, "Failed to fetch teams")

    teams = response.json()
    dump_json_if_debug_enabled(teams)

    # Cache the newly fetched data with a 24-hour expiry
    cache_json("teams", {}, 24 * 60 * 60, teams)

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
