from typing import Tuple, List, Iterable, Dict
import logging
from datetime import datetime, timedelta
import requests
from nhltv_lib.arguments import get_arguments
from nhltv_lib.urls import get_schedule_url_between_dates
from nhltv_lib.downloaded_games import get_downloaded_games
from nhltv_lib.waitlist import get_blackout_wait_list
from nhltv_lib.teams import get_team
from nhltv_lib.common import dump_json_if_debug_enabled
from nhltv_lib.types import Game, GameDict


def get_checkinterval() -> int:
    """
    Get checkinterval from parsed args
    """
    arguments = get_arguments()

    try:
        return int(arguments.checkinterval)
    except TypeError:
        return 10


def get_games_to_download() -> Tuple[Game, ...]:
    """
    Gets all the games that are available to be downloaded and matches
    the criteria (eg. correct team, not already downloaded etc.)
    """
    start_date: str = get_start_date()
    end_date: str = get_end_date()

    all_games: dict = fetch_games(
        get_schedule_url_between_dates(start_date, end_date)
    )

    dump_json_if_debug_enabled(all_games)

    games_objects: Iterable[Game] = create_game_objects(
        tuple(filter_games(all_games))
    )

    return tuple(games_objects)


def get_start_date() -> str:
    """
    Get isoformatted date from which to start searching
    """
    days_back: int = get_days_back()

    current_time: datetime = datetime.now()
    return (current_time.date() - timedelta(days=days_back)).isoformat()


def get_days_back() -> int:
    """
    Get the amount of days to go back in searching, as supplied to command line
    """
    arguments = get_arguments()

    try:
        return int(arguments.days_back_to_search)
    except TypeError:
        return 3


def get_end_date() -> str:
    """
    Get the date on which to end the search, i.e. today, isoformatted
    """
    current_time = datetime.now()
    return current_time.date().isoformat()


def fetch_games(url: str) -> dict:
    """
    Gets all games from the NHL API
    """
    logger = logging.getLogger("nhltv")
    logger.debug("Looking up games @ %s", url)
    return requests.get(url).json()


def filter_games(games: Dict[str, List[GameDict]]) -> Iterable[GameDict]:
    """
    Calls all other filter functions and returns what is left
    """
    games_w_team = filter_games_with_team(games)
    games_started = filter_games_that_have_not_started(games_w_team)
    not_downloaded = filter_games_already_downloaded(games_started)
    no_duplicates = filter_duplicates(not_downloaded)
    no_blackout_wait = filter_games_on_blackout_waitlist(no_duplicates)
    return no_blackout_wait


def filter_games_that_have_not_started(
    games: Iterable[GameDict]
) -> Iterable[GameDict]:
    return filter(
        lambda x: datetime.fromisoformat(x["gameDate"].strip("Z"))
        < datetime.now(),
        games,
    )


def filter_games_with_team(
    all_games: Dict[str, List[GameDict]]
) -> Tuple[GameDict, ...]:
    """
    Filters out any games that do not contain the correct team
    """
    games: List[GameDict] = []

    for date in all_games["dates"]:
        games_on_date = date["games"]
        games_with_team = list(
            filter(check_if_game_involves_team, games_on_date)
        )
        if games_with_team:
            games += games_with_team

    return tuple(games)


def check_if_game_involves_team(game: GameDict) -> bool:
    """
    Returns true if a given game contains our team
    """
    team_id = get_team_id()
    return team_id in (
        game["teams"]["home"]["team"]["id"],
        game["teams"]["away"]["team"]["id"],
    )


def filter_games_already_downloaded(
    games: Iterable[GameDict]
) -> Iterable[GameDict]:
    """
    Filter out games that have already been downloaded
    """
    return filter(check_if_game_is_downloaded, games)


def check_if_game_is_downloaded(game: GameDict) -> bool:
    """
    Returns true if the game has not been downloaded already
    """
    downloaded_games = get_downloaded_games()
    return game["gamePk"] not in downloaded_games


def filter_duplicates(games: Iterable[GameDict]) -> Tuple[GameDict, ...]:
    """
    Filters out any duplicate games by game_id (gamePk)
    """
    new_games: List[GameDict] = []
    added_ids: List[int] = []
    for game in games:
        if game["gamePk"] not in added_ids:
            added_ids.append(game["gamePk"])
            new_games.append(game)
    return tuple(new_games)


def filter_games_on_blackout_waitlist(
    games: Iterable[GameDict]
) -> Iterable[GameDict]:
    """
    Filter out games that have been added to the blackout waitlist
    """
    return filter(
        lambda x: str(x["gamePk"]) not in get_blackout_wait_list().keys(),
        games,
    )


def create_game_objects(games: Tuple[GameDict, ...]) -> Iterable[Game]:
    """
    Creates game objects from a list of games
    """
    return map(create_game_object, games)


def create_game_object(game: GameDict) -> Game:
    """
    Returns a game object from a single game dict
    """
    return Game(
        game["gamePk"],
        is_home_game(game),
        game["content"]["media"]["epg"][0]["items"],
    )


def is_home_game(game: GameDict) -> bool:
    """
    Returns True if this game is a home game for our team
    """
    team_id = get_team_id()
    return team_id == game["teams"]["home"]["team"]["id"]


def get_team_id() -> int:
    """
    Returns the id of our team, as supplied as command line argument
    """
    arguments = get_arguments()
    return get_team(arguments.team)
