import os
import inspect
import logging
from shutil import move
from pathlib import Path
import json
import pickle
from datetime import datetime
from nhltv_lib.arguments import get_arguments
from nhltv_lib.settings import get_download_folder

logger = logging.getLogger("nhltv")


def touch(filename):
    if not os.path.isfile(filename):
        Path(filename).touch()


def print_progress_bar(
    iteration, total, prefix="", suffix="", decimals=1, length=50, fill="█"
):
    """
    Prints an updatable terminal progress bar
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total))
    )
    filled = int(length * iteration // total)
    bar_ = fill * filled + "-" * (length - filled)
    print("\r%s |%s| %s%% %s" % (prefix, bar_, percent, suffix), end="\r")

    if iteration == total:
        print()


def debug_dumps_enabled():
    arguments = get_arguments()

    if arguments.debug_dumps_enabled:
        if not os.path.isdir("dumps"):
            os.mkdir("dumps")

    return arguments.debug_dumps_enabled


def debug_dump_json(content, caller=""):
    filename = f"dumps/{caller}_{datetime.now().isoformat()}.json"
    with open(filename, "w") as f:
        json.dump(content, f)


def debug_dump_pickle(content, caller=""):
    filename = f"dumps/{caller}_{datetime.now().isoformat()}.pickle"
    with open(filename, "wb") as f:
        pickle.dump(content, f)


def dump_json_if_debug_enabled(content):
    caller_name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    if debug_dumps_enabled():
        debug_dump_json(content, caller=caller_name)


def dump_pickle_if_debug_enabled(content):
    caller_name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    if debug_dumps_enabled():
        debug_dump_pickle(content, caller=caller_name)


def move_file_to_download_folder(download):
    """
    Moves the final product to the DOWNLOAD_FOLDER
    """
    input_file = f"{download.game_id}_ready.mkv"

    download_dir = get_download_folder()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    logger.debug("Moving final to video to %s", download_dir)
    output_file = f"{download_dir}/{download.game_info}.mkv"
    move(input_file, output_file)


def write_lines_to_file(lines, file_):
    with open(file_, "w") as f:
        f.writelines(lines)


def read_lines_from_file(file_):
    with open(file_, "r") as f:
        return f.readlines()
