from typing import Union
import requests
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
    return requests.get(TEAMS_URL).json()


def find_team_by_id(team_id: int) -> int:
    team_json = fetch_teams()
    return list(filter(lambda x: x["id"] == team_id, team_json["teams"]))[0][
        "id"
    ]


def find_team_by_abbreviation(abbreviation: str) -> int:
    team_json = fetch_teams()
    return list(
        filter(lambda x: x["abbreviation"] == abbreviation, team_json["teams"])
    )[0]["id"]


def find_team_by_name(name: str) -> int:
    team_json = fetch_teams()
    return list(filter(lambda x: x["name"] == name, team_json["teams"]))[0][
        "id"
    ]
