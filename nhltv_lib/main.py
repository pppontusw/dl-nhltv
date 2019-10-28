import sys
import logging
import argparse
from nhltv_lib.auth import NHLTVUser
from nhltv_lib.logger import setup_logging
from nhltv_lib.settings import get_settings_from_arguments


def parse_args(args):
    parser = argparse.ArgumentParser(description="%(prog)s: Download NHL TV")

    parser.add_argument(
        "-u",
        "--username",
        dest="username",
        help="Username of your NHLTV account",
        required=True,
    )

    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="Password of your NHLTV account",
        required=True,
    )

    parser.add_argument(
        "-q",
        "--quality",
        dest="quality",
        help="is highest by default you can set it to 5000, 3500, 1500, 900",
    )

    parser.add_argument(
        "-d",
        "--download_folder",
        dest="download_folder",
        help="Output folder where you want to store your final file like $HOME/Desktop/NHL/",
    )

    parser.add_argument(
        "-i",
        "--checkinterval",
        dest="checkinterval",
        help="Specify checkinterval in minutes to look for new games, default is 60",
    )

    parser.add_argument(
        "-k",
        "--keep",
        dest="retentiondays",
        help="Specify how many days video and download logs are kept, default is forever",
    )

    parser.add_argument(
        "-b",
        "--days-back",
        dest="days_back_to_search",
        help="Specify how many days to go back when looking for a game, default is 3",
    )

    parser.add_argument(
        "-o",
        "--obfuscate",
        dest="obfuscate",
        action="store_true",
        help="Obfuscate the ending time of the video (pads the video end with black video)",
    )

    parser.add_argument(
        "--short-debug",
        dest="shorten_video",
        action="store_true",
        help="Shorten video length to just a few minutes for debugging purposes",
    )

    return parser.parse_args(args)


def main():
    arguments = parse_args(sys.argv[1:])

    setup_logging()
    logger = logging.getLogger("nhltv")

    nhltv_user = NHLTVUser(arguments.username, arguments.password)
    logger.debug("Set nhltv_user to %s", nhltv_user)

    settings = get_settings_from_arguments(arguments)
    logger.error("Settings set to %s", settings)


if __name__ == "__main__":
    main()
