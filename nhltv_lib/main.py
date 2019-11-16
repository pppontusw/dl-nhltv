from time import sleep
import logging
from nhltv_lib.logger import setup_logging
from nhltv_lib.process import verify_cmd_exists_in_path
from nhltv_lib.game import get_games_to_download
from nhltv_lib.stream import get_streams_to_download
from nhltv_lib.download import download_game
from nhltv_lib.auth import login_and_save_cookie
from nhltv_lib.exceptions import AuthenticationFailed
from nhltv_lib.obfuscate import obfuscate

logger = logging.getLogger("nhltv")


def verify_dependencies():
    dependent_commands = ["ffmpeg", "aria2c"]

    for i in dependent_commands:
        verify_cmd_exists_in_path(i)


def main():

    setup_logging()
    verify_dependencies()

    login_and_save_cookie()

    games_to_download = get_games_to_download()

    streams = get_streams_to_download(games_to_download)

    try:
        download_game(streams[0])
        obfuscate(streams[0])
    except AuthenticationFailed:
        sleep(300)
        return main()


if __name__ == "__main__":
    main()
