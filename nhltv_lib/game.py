from typing import Tuple, List, Iterable, Dict
from datetime import datetime, timedelta, UTC
from nhltv_lib.auth import get_auth_cookie_value
from nhltv_lib.constants import HEADERS
import nhltv_lib.requests_wrapper as requests
from nhltv_lib.arguments import get_arguments
from nhltv_lib.urls import get_schedule_url_between_dates
from nhltv_lib.teams import get_team
from nhltv_lib.common import dump_json_if_debug_enabled, tprint
from nhltv_lib.types import Game, GameDict
import nhltv_lib.game_tracking as game_tracking
from nhltv_lib.models import DbGame


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

    filtered_games = tuple(filter_games(all_games))

    games_objects: Iterable[Game] = create_game_objects(filtered_games)
    add_games_to_tracking(filtered_games)

    games_list: Tuple[Game, ...] = tuple(games_objects)
    game_ids: List[int] = [i.game_id for i in games_list]

    tprint(f"Found games {game_ids}", debug_only=True)

    return games_list


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
    tprint("Looking up games..")
    tprint(f"@ {url}", debug_only=True)

    return requests.get(url, headers={**HEADERS}).json()


def filter_games(games: Dict[str, List[GameDict]]) -> Iterable[GameDict]:
    """
    Calls all other filter functions and returns what is left
    """
    games_w_team = filter_games_with_team(games)
    games_started = filter_games_that_have_not_started(games_w_team)
    not_downloaded = filter_games_already_downloaded(games_started)
    no_duplicates = filter_duplicates(not_downloaded)
    no_blackout_wait = filter_games_in_waiting(no_duplicates)
    return no_blackout_wait


def filter_games_that_have_not_started(
    games: Iterable[GameDict]
) -> Iterable[GameDict]:
    return filter(
        lambda x: datetime.fromisoformat(x["startTime"])
        < datetime.now(UTC),
        games,
    )


def filter_games_with_team(
    all_games: Dict[str, List[GameDict]]
) -> Tuple[GameDict, ...]:
    """
    Filters out any games that do not contain the correct team
    """
    games: List[GameDict] = []

    for game in all_games["data"]:
        games_with_team = list(
            filter(check_if_game_involves_team, [game])
        )
        if games_with_team:
            games += games_with_team

    return tuple(games)


def check_if_game_involves_team(game: GameDict) -> bool:
    """
    Returns true if a given game contains our team
    """
    team_id = get_team_id()
    return str(team_id) in (
        game["homeCompetitor"]["externalId"],
        game["awayCompetitor"]["externalId"],
    )


def filter_games_already_downloaded(
    games: Iterable[GameDict]
) -> Iterable[GameDict]:
    """
    Filter out games that have already been downloaded
    """
    return filter(check_if_game_is_not_already_downloaded, games)


def check_if_game_is_not_already_downloaded(game: GameDict) -> bool:
    """
    Returns false if the game has already been downloaded
    """
    return game_tracking.game_not_downloaded(game["id"])


def filter_duplicates(games: Iterable[GameDict]) -> Tuple[GameDict, ...]:
    """
    Filters out any duplicate games by game_id
    """
    new_games: List[GameDict] = []
    added_ids: List[int] = []
    for game in games:
        if game["id"] not in added_ids:
            added_ids.append(game["id"])
            new_games.append(game)
    return tuple(new_games)


def filter_games_in_waiting(games: Iterable[GameDict]) -> Iterable[GameDict]:
    """
    Filter out games that we need to wait on (ex. blackout)
    """
    return filter(
        lambda x: game_tracking.ready_for_next_attempt(x["id"]), games
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
    streams = [stream for stream in game["content"] if stream["contentType"]["name"] == "Full Game"]
    return Game(
        game["id"],
        is_home_game(game),
        streams,
    )


def add_games_to_tracking(games: Tuple[GameDict, ...]) -> List[DbGame]:
    """
    Creates games in the database from a list of games
    """
    return list(map(add_game_to_tracking, games))


def add_game_to_tracking(gamedict: GameDict) -> DbGame:

    home_team = gamedict["homeCompetitor"]["name"]
    away_team = gamedict["awayCompetitor"]["name"]

    game = game_tracking.start_tracking_game(
        gamedict["id"],
        datetime.fromisoformat(gamedict["startTime"]),
        home_team,
        away_team,
    )
    return game


def is_home_game(game: GameDict) -> bool:
    """
    Returns True if this game is a home game for our team
    """
    team_id = get_team_id()
    return str(team_id) == game["homeCompetitor"]["externalId"]


def get_team_id() -> int:
    """
    Returns the id of our team, as supplied as command line argument
    """
    arguments = get_arguments()
    return get_team(arguments.team)
