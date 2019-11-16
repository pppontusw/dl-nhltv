import os
from shutil import move
import json
import pickle
from uuid import uuid4
from nhltv_lib.arguments import get_arguments
from nhltv_lib.settings import get_download_folder
from nhltv_lib.process import call_subprocess_and_raise_on_error


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

    return arguments.debug_dumps_enabled


def debug_dump_json(content):
    filename = f"{uuid4()}.json"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            json.dump(content, f)


def debug_dump(content):
    filename = f"{uuid4()}.txt"
    if not os.path.exists(filename):
        with open(filename, "wb") as f:
            pickle.dump(content, f)


def dump_json_if_debug_enabled(content):
    if debug_dumps_enabled():
        debug_dump_json(content)


def dump_pickle_if_debug_enabled(content):
    if debug_dumps_enabled():
        debug_dump(content)


def move_file_to_download_folder(download):
    """
    Moves the final product to the DOWNLOAD_FOLDER
    """
    inputFile = f"{download.game_id}_ready.mkv"
    download_dir = get_download_folder()
    outputFile = f"{download_dir}/{download.game_info}.mkv"
    # Create the download directory if required
    command = "mkdir -p $(dirname " + outputFile + ")"
    call_subprocess_and_raise_on_error(command)
    move(inputFile, outputFile)
