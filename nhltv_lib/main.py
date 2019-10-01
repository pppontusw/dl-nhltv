import argparse
import os
import time
import glob
from nhltv_lib.download_nhl import DownloadNHL
from nhltv_lib.common import tprint, get_setting, which, wait, set_setting
from nhltv_lib.teams import Teams
from nhltv_lib.video import reEncode
from nhltv_lib.exceptions import BlackoutRestriction, NoGameFound

TEAMIDS = []


__author__ = "Clayton Maxwell && Helge Wehder && loopway && Pontus Wiberg"


def download_game(TEAM):

    download_folder = get_setting("DOWNLOAD_FOLDER", "GLOBAL")

    try:
        dl = DownloadNHL(TEAM.id)
        dl.get_next_game()
        dl.fetch_stream()
    except NoGameFound:
        tprint("No new game.")
        return False
    except BlackoutRestriction:
        wait(
            reason="Game is effected by NHL Game Center blackout restrictions.",
            minutes=12 * 60,
        )

    tprint("Downloading stream_url")
    outputFile = str(dl.game_id) + "_raw.mkv"
    dl.download_nhl(dl.stream_url, outputFile)

    # Remove silence
    tprint("Removing silence...")
    dl.skip_silence(outputFile)

    if get_setting("OBFUSCATE", "GLOBAL") is True:
        tprint("Obfuscating end time of the video")
        obf_outputFile = outputFile.replace("raw", "obf")
        dl.obfuscate(outputFile, obf_outputFile)
        outputFile = obf_outputFile

    newFileName = (
        download_folder
        + "/"
        + str(TEAM.abbreviation)
        + "_"
        + dl.game_info
        + "_"
        + str(dl.game_id)
        + ".mkv"
    )
    dl.move_file(outputFile, newFileName)

    if get_setting("MOBILE_VIDEO", "GLOBAL") is True:
        tprint("Re-encoding for phone...")
        reEncode(newFileName, str(dl.game_id) + "_phone.mkv")

    # Update the settings to reflect that the game was downloaded
    set_setting("lastGameID", dl.game_id, TEAM.id)

    dl.clean_up()
    return download_game(TEAM)


def main():
    """
    Find the game_id or wait until one is ready
    """
    while True:
        download_folder = get_setting("DOWNLOAD_FOLDER", "GLOBAL")

        for TEAMID in TEAMIDS:
            download_game(TEAMID)

        retention_days = get_setting("RETENTIONDAYS", "GLOBAL")
        if retention_days:
            tprint("Running housekeeping ...")
            pathpattern = (download_folder + "/*.mkv", "*.mkv_download.log")
            now = time.time()
            for pp in pathpattern:
                for f in glob.glob(pp):
                    if os.stat(f).st_mtime < now - retention_days * 86400:
                        tprint("deleting " + f + "...")
                        os.remove(f)

        check_interval = get_setting("CHECKINTERVAL", "GLOBAL")
        wait(
            reason="Checking for new games again in "
            + str(check_interval)
            + " hours ...",
            minutes=check_interval * 60,
        )


def parse_args():

    if which("ffmpeg") is False:
        print("Missing ffmpeg command please install or check PATH exiting...")
        exit(1)

    if which("aria2c") is False:
        print("Missing aria2c command please install or check PATH exiting...")
        exit(1)

    parser = argparse.ArgumentParser(description="%(prog)s: Download NHL TV")

    parser.add_argument(
        "-t",
        "--team",
        "--append-action",
        action="append",
        dest="TEAMID",
        help="Team ID i.e. 17 or DET or Detroit, can be used multiple times",
        required=True,
    )

    parser.add_argument(
        "-u", "--username", dest="USERNAME", help="User name of your NHLTV account"
    )

    parser.add_argument(
        "-p", "--password", dest="PASSWORD", help="Password of your NHL TV account "
    )

    parser.add_argument(
        "-q",
        "--quality",
        dest="QUALITY",
        help="is highest by default you can set it to 5000, 3500, 1500, 900",
    )

    parser.add_argument(
        "-d",
        "--download_folder",
        dest="DOWNLOAD_FOLDER",
        help="Output folder where you want to store your final file like $HOME/Desktop/NHL/",
    )

    parser.add_argument(
        "-i",
        "--checkinterval",
        dest="CHECKINTERVAL",
        help="Specify checkinterval in hours to look for new games, default is 4",
    )

    parser.set_defaults(feature=True)
    parser.add_argument(
        "-r",
        "--retry",
        dest="RETRY_ERRORED_DOWNLOADS",
        action="store_true",
        help="Usually works fine without, Use this flag if you want it perfect",
    )

    parser.add_argument(
        "-m",
        "--mobile_video",
        dest="MOBILE_VIDEO",
        action="store_true",
        help="Set this to also encode video for mobile devices",
    )

    parser.add_argument(
        "-k",
        "--keep",
        dest="RETENTIONDAYS",
        help="Specify how many days video and download logs are kept, default is forever",
    )

    parser.add_argument(
        "-b",
        "--days-back",
        dest="DAYSBACK",
        help="Specify how many days to go back when looking for a game, default is 3",
    )

    parser.add_argument(
        "-o",
        "--obfuscate",
        dest="OBFUSCATE",
        action="store_true",
        help="Obfuscate the ending time of the video (pads the video end with black video)",
    )

    parser.add_argument(
        "--debug", dest="DEBUG", action="store_true", help="Debug (shorten video)"
    )

    args = parser.parse_args()

    if args.TEAMID:
        for TEAMID in args.TEAMID:
            teams = Teams()
            team = teams.getTeam(TEAMID)
            TEAMIDS.append(team)

    if args.USERNAME:
        set_setting("USERNAME", args.USERNAME, "GLOBAL")

    if args.PASSWORD:
        set_setting("PASSWORD", args.PASSWORD, "GLOBAL")

    if args.QUALITY:
        set_setting("QUALITY", args.QUALITY, "GLOBAL")
    else:
        if not get_setting("QUALITY", "GLOBAL"):
            set_setting("QUALITY", "5600", "GLOBAL")

    if args.DOWNLOAD_FOLDER:
        DOWNLOAD_FOLDER = args.DOWNLOAD_FOLDER
        set_setting("DOWNLOAD_FOLDER", DOWNLOAD_FOLDER, "GLOBAL")
    else:
        set_setting("DOWNLOAD_FOLDER", "./", "GLOBAL")

    if args.CHECKINTERVAL:
        set_setting("CHECKINTERVAL", int(args.CHECKINTERVAL), "GLOBAL")
    else:
        if not get_setting("CHECKINTERVAL", "GLOBAL"):
            set_setting("CHECKINTERVAL", 4, "GLOBAL")

    if args.RETRY_ERRORED_DOWNLOADS:
        set_setting("RETRY_ERRORED_DOWNLOADS", args.RETRY_ERRORED_DOWNLOADS, "GLOBAL")

    if args.MOBILE_VIDEO:
        set_setting("MOBILE_VIDEO", args.MOBILE_VIDEO, "GLOBAL")

    if args.RETENTIONDAYS:
        set_setting("RETENTIONDAYS", int(args.RETENTIONDAYS), "GLOBAL")

    if args.DAYSBACK:
        set_setting("DAYSBACK", int(args.DAYSBACK), "GLOBAL")
    else:
        set_setting("DAYSBACK", 3, "GLOBAL")

    if args.OBFUSCATE:
        set_setting("OBFUSCATE", True, "GLOBAL")
    else:
        set_setting("OBFUSCATE", False, "GLOBAL")

    if args.DEBUG:
        set_setting("DEBUG", True, "GLOBAL")
    else:
        set_setting("DEBUG", False, "GLOBAL")

    while True:
        main()


if __name__ == "__main__":
    parse_args()
