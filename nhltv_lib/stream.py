import logging
from itertools import filterfalse
from collections import namedtuple
from nhltv_lib.arguments import get_arguments
from nhltv_lib.waitlist import (
    get_archive_wait_list,
    add_game_to_archive_wait_list,
)

logger = logging.getLogger("nhltv")

Stream = namedtuple("Stream", ["game_id", "content_id", "event_id"])


def get_streams_to_download(games):
    games_not_ready_yet = filterfalse(is_ready_to_download, games)
    mark_unarchived_games_to_wait(games_not_ready_yet)

    games_ready_to_download = filter(is_ready_to_download, games)
    stream_objects = create_stream_objects(games_ready_to_download)

    return list(stream_objects)


def create_stream_objects(games):
    return map(create_stream_object, games)


def create_stream_object(game):
    best_stream = get_best_stream(game)
    return Stream(
        game.game_id, best_stream["mediaPlaybackId"], best_stream["eventId"]
    )


def get_best_stream(game):
    best_stream = None
    best_score = -1

    for stream in game.streams:
        score = 0
        if stream["language"] == "eng":
            score += 100
        if stream_matches_home_away(game, stream["mediaFeedType"]):
            score += 50
        if score > best_score:
            best_score = score
            best_stream = stream

    return best_stream


def is_ready_to_download(stream):
    return (
        len(
            [
                i
                for i in stream.streams
                if i.get("mediaState", "") == "MEDIA_ARCHIVE"
            ]
        )
        > 0
    )


def stream_matches_home_away(game, stream_type):
    """
    Checks if team.home=stream.home or team.away=stream.away
    """
    return (game.is_home_game and stream_type == "HOME") or (
        not game.is_home_game and stream_type == "AWAY"
    )


def mark_unarchived_games_to_wait(games):
    unarchived_games_list = get_archive_wait_list()
    for game in games:
        if str(game.game_id) not in unarchived_games_list.keys():
            add_game_to_archive_wait_list(game.game_id)


def get_quality():
    """
    Get quality from parsed args
    """
    args = get_arguments()

    if not args.quality:
        quality = 5000
    else:
        quality = int(args.quality)

    return quality


def get_shorten_video():
    """
    Are we shortening the video?
    """
    args = get_arguments()

    return args.shorten_video


