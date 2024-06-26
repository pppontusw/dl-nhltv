from typing import List, Iterable, Tuple
from nhltv_lib.cache import cache_json, load_cache_json
from nhltv_lib.requests_wrapper import requests
from nhltv_lib.common import (
    dump_json_if_debug_enabled,
    tprint,
    verify_request_200,
)
from nhltv_lib.arguments import get_arguments
from nhltv_lib.constants import HEADERS
from nhltv_lib.types import NHLStream, Game
from nhltv_lib.urls import get_player_settings_url


def get_streams_to_download(games: Tuple[Game, ...]) -> List[NHLStream]:
    games_ready_to_download: Iterable[Game] = filter(
        is_ready_to_download, games
    )
    stream_objects: Iterable[NHLStream] = create_stream_objects(
        games_ready_to_download
    )

    return list(stream_objects)


def create_stream_objects(games: Iterable[Game]) -> Iterable[NHLStream]:
    return map(create_stream_object, games)


def create_stream_object(game: Game) -> NHLStream:
    best_stream = get_best_stream(game)
    best_stream_settings = get_stream_settings(best_stream)
    return NHLStream(game.game_id, best_stream, best_stream_settings)


def get_stream_settings(stream: dict) -> dict:
    """Fetch or retrieve from cache the stream settings based on stream ID.

    Args:
        stream (dict): Dictionary containing a NHL TV stream.

    Returns:
        dict: The stream settings.

    Raises:
        FetchError: If the response from the server is not successful.
    """
    cache_name = f"stream_{stream['id']}"
    params = {"url": get_player_settings_url(stream["id"])}

    # Attempt to load from cache first
    cached_settings = load_cache_json(cache_name, params)
    if cached_settings is not None:
        return cached_settings

    # If not cached, fetch from the server
    response = requests.get(params["url"], headers=HEADERS, timeout=15)
    verify_request_200(
        response, f"Failed to get stream settings for stream {stream['id']}"
    )

    settings = response.json()
    # Cache the fetched data
    cache_json(
        name=cache_name, parameters=params, expires_in=300, content=settings
    )

    dump_json_if_debug_enabled(settings)

    return settings


def get_best_stream(game: Game) -> dict:
    best_stream: dict = {}
    best_score: int = -1

    for stream in game.streams:
        dump_json_if_debug_enabled(stream)
        score: int = 0
        if stream_matches_home_away(
            game, stream["clientContentMetadata"][0].get("name")
        ):
            score += 50
        if score > best_score:
            best_score = score
            best_stream = stream

    # if our preferred stream cannot be downloaded, set the best stream to {}
    # and say this game is not yet ready to be downloaded
    if not get_stream_settings(best_stream)["isDelivered"]:
        tprint(
            f"Stream was found for game {game.game_id} that is "
            f"not archived yet, waiting.."
        )
        best_stream = {}

    return best_stream


def is_ready_to_download(game: Game) -> bool:
    return get_best_stream(game) != {}


def stream_matches_home_away(game: Game, stream_type: str) -> bool:
    """
    Checks if team.home=stream.home or team.away=stream.away
    """
    return (game.is_home_game and stream_type == "HOME") or (
        not game.is_home_game and stream_type == "AWAY"
    )


def get_shorten_video() -> bool:
    """
    Are we shortening the video?
    """
    args = get_arguments()

    return args.shorten_video
