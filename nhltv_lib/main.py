import logging
from nhltv_lib.auth import NHLTVUser
from nhltv_lib.logger import setup_logging
from nhltv_lib.arguments import get_arguments
from nhltv_lib.process import verify_cmd_exists_in_path
from nhltv_lib.game import get_games_to_download
from nhltv_lib.stream import get_streams_to_download
from nhltv_lib.download import get_downloads_from_streams, download_game
from nhltv_lib.auth import login_and_save_cookie

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

    print(games_to_download)

    streams = get_streams_to_download(games_to_download)

    print(streams)

    downloads = get_downloads_from_streams(streams)

    print(downloads)
    download_game(downloads)


if __name__ == "__main__":
    main()
