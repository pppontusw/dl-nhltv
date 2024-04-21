from typing import List
import argparse
import sys


def get_arguments() -> argparse.Namespace:
    return parse_args(sys.argv[1:])


def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="%(prog)s: Download NHL TV")

    parser.add_argument(
        "-t",
        "--team",
        dest="team",
        help="Team name or ID - example: Nashville Predators, NSH or 18",
        required=True,
    )

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
        "-d",
        "--download_folder",
        dest="download_folder",
        help="Final video destination e.g. $HOME/Desktop/NHL/",
    )

    parser.add_argument(
        "-i",
        "--checkinterval",
        dest="checkinterval",
        help="Interval in minutes to look for new games (default: 10)",
    )

    parser.add_argument(
        "-k",
        "--keep",
        dest="retentiondays",
        help="How many days video and logs are kept (default: forever)",
    )

    parser.add_argument(
        "-b",
        "--days-back",
        dest="days_back_to_search",
        help="How many days back to search (default: 3)",
    )

    parser.add_argument(
        "--short-debug",
        dest="shorten_video",
        action="store_true",
        help="Shorten video length to just a few minutes for debugging",
    )

    parser.add_argument(
        "--debug",
        "--debug-dumps",
        dest="debug_dumps_enabled",
        action="store_true",
        help="Enable debugging -- adds extra logging and debug dumps in the ./dumps folder",
    )

    return parser.parse_args(args)
