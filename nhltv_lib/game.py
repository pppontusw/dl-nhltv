import logging
from datetime import datetime, timedelta
from collections import namedtuple
import requests
from nhltv_lib.arguments import get_arguments
from nhltv_lib.urls import get_schedule_url_between_dates

Game = namedtuple(
    "Game", ["game_id", "is_home_game", "content_id", "game_info"]
)


def get_checkinterval():
    """
    Get checkinterval from parsed args
    """
    arguments = get_arguments()

    return int(arguments.checkinterval) or 60


def get_next_game():
    start_date = get_start_date()
    end_date = get_end_date()

    all_games = fetch_games(
        get_schedule_url_between_dates(start_date, end_date)
    )

    games_with_team = filter_games_with_team(all_games)

    # TODO: filter out games already downloaded

    # TODO: sort and return 1st

    return games_with_team


def get_start_date():
    days_back = get_days_back()

    current_time = datetime.now()
    return (current_time.date() - timedelta(days=days_back)).isoformat()


def get_end_date():
    current_time = datetime.now()
    return current_time.date().isoformat()


def fetch_games(url):
    logger = logging.getLogger("nhltv")
    logger.debug("Looking up games @ %s", url)
    return requests.get(url).json()


def filter_games_with_team(all_games):
    games = []

    for date in all_games["dates"]:
        games_on_date = date["games"]
        games_with_team = list(
            filter(check_if_game_involves_team, games_on_date)
        )
        if games_with_team:
            games += games_with_team

    return games


def check_if_game_involves_team(game):
    team_id = get_team_id()
    return team_id in (
        game["teams"]["home"]["team"]["id"],
        game["teams"]["away"]["team"]["id"],
    )


def get_team_id():
    return 18


def get_days_back():
    """
    Get days_back_to_search from parsed args
    """
    arguments = get_arguments()

    return int(arguments.days_back_to_search) or 3
