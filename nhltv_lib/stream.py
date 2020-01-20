from typing import List, Iterable, Tuple
import logging
from nhltv_lib.arguments import get_arguments
from nhltv_lib.types import Stream, Game

logger = logging.getLogger("nhltv")


def get_streams_to_download(games: Tuple[Game, ...]) -> List[Stream]:
    games_ready_to_download: Iterable[Game] = filter(
        is_ready_to_download, games
    )
    stream_objects: Iterable[Stream] = create_stream_objects(
        games_ready_to_download
    )

    return list(stream_objects)


def create_stream_objects(games: Iterable[Game]) -> Iterable[Stream]:
    return map(create_stream_object, games)


def create_stream_object(game: Game) -> Stream:
    best_stream: dict = get_best_stream(game)
    return Stream(
        game.game_id, best_stream["mediaPlaybackId"], best_stream["eventId"]
    )


def get_best_stream(game: Game) -> dict:
    best_stream: dict = {}
    best_score: int = -1

    for stream in game.streams:
        score: int = 0
        if stream.get("callLetters", "") in get_preferred_streams():
            score += 1000
        if stream["language"] == "eng":
            score += 100
        if stream_matches_home_away(game, stream["mediaFeedType"]):
            score += 50
        if score > best_score:
            best_score = score
            best_stream = stream

    # if our preferred stream cannot be downloaded, set the best stream to {}
    # and say this game is not yet ready to be downloaded
    if best_stream.get("mediaState", "") != "MEDIA_ARCHIVE":
        logger.debug(
            "Stream was found for game %s that is not archived yet, waiting..",
            game.game_id,
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


def get_quality() -> int:
    """
    Get quality from parsed args
    """
    args = get_arguments()

    if not args.quality:
        quality = 5000
    else:
        quality = int(args.quality)

    return quality


def get_shorten_video() -> bool:
    """
    Are we shortening the video?
    """
    args = get_arguments()

    return args.shorten_video


def get_preferred_streams() -> List[str]:
    args = get_arguments()

    if args.preferred_stream is None:
        return []
    else:
        return args.preferred_stream
