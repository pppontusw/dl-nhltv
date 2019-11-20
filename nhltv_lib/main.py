from typing import Tuple, List
from time import sleep
import logging
from nhltv_lib.logger import setup_logging
from nhltv_lib.process import verify_cmd_exists_in_path
from nhltv_lib.game import get_games_to_download, get_checkinterval
from nhltv_lib.stream import get_streams_to_download
from nhltv_lib.download import download_game, clean_up_download
from nhltv_lib.skip_silence import skip_silence
from nhltv_lib.auth import (
    login_and_save_cookie,
    get_auth_cookie_expires_in_minutes,
)
from nhltv_lib.exceptions import AuthenticationFailed, BlackoutRestriction
from nhltv_lib.obfuscate import obfuscate
from nhltv_lib.waitlist import add_game_to_blackout_wait_list
from nhltv_lib.downloaded_games import add_to_downloaded_games
from nhltv_lib.types import Download, Stream, Game

logger = logging.getLogger("nhltv")


def verify_dependencies() -> None:
    """
    Verifies that required external tools are present
    """
    dependent_commands = ["ffmpeg", "aria2c"]

    for i in dependent_commands:
        verify_cmd_exists_in_path(i)


def main() -> None:
    """
    Sets up the application and starts the main loop
    """

    setup_logging()
    verify_dependencies()

    login_and_save_cookie()

    run_loop()


def run_loop() -> None:
    while True:
        loop()


def loop() -> None:
    get_and_download_games()
    check_interval = get_checkinterval()
    logger.debug(
        "No games to dowload, waiting %d minutes before checking again..",
        check_interval,
    )
    sleep(check_interval * 60)

    # check if we need to refresh the login (auth cookie)
    cookie_expiration = get_auth_cookie_expires_in_minutes()
    if cookie_expiration is None or cookie_expiration < 30:
        login_and_save_cookie()


def get_and_download_games() -> None:
    """
    Gets all games that matches criteria and starts downloading them
    """
    games_to_download: Tuple[Game, ...] = get_games_to_download()

    streams: List[Stream] = get_streams_to_download(games_to_download)

    for i in streams:
        download(i)


def download(stream: Stream) -> None:
    """
    Loop for downloading a single game, retrying if authentication fails
    """
    try:
        dl: Download = download_game(stream)
        skip_silence(dl)
        obfuscate(dl)
        clean_up_download(dl.game_id, delete_cookie=True)
        add_to_downloaded_games(dl.game_id)
    except AuthenticationFailed:
        sleep(300)
        return download(stream)
    except BlackoutRestriction:
        add_game_to_blackout_wait_list(stream.game_id)


if __name__ == "__main__":
    main()
