import argparse
import sys


def get_arguments():
    return parse_args(sys.argv[1:])


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
        help="5000, 3500, 1500, 900 (default: 5000)",
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
        help="Interval in minutes to look for new games (default: 60)",
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
        "-o",
        "--obfuscate",
        dest="obfuscate",
        action="store_true",
        help="Obfuscate the ending time of the video",
    )

    parser.add_argument(
        "--short-debug",
        dest="shorten_video",
        action="store_true",
        help="Shorten video length to just a few minutes for debugging",
    )

    return parser.parse_args(args)
