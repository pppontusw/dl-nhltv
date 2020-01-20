from typing import Union, List, Dict, Any
import os
import inspect
from shutil import move
from pathlib import Path
import json
import pickle
from datetime import datetime
from nhltv_lib.arguments import get_arguments
from nhltv_lib.settings import get_download_folder
from nhltv_lib.types import Download


def touch(filename: str) -> None:
    if not os.path.isfile(filename):
        Path(filename).touch()


def print_progress_bar(
    iteration: int,
    total: int,
    prefix: str = "",
    suffix: str = "",
    decimals: int = 1,
    length: int = 50,
    fill: str = "█",
) -> None:
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


def debug_dumps_enabled() -> bool:
    arguments = get_arguments()

    if arguments.debug_dumps_enabled and not os.path.isdir("dumps"):
        os.mkdir("dumps")

    return arguments.debug_dumps_enabled


def debug_dump_json(content: Union[dict, list], caller: str = "") -> None:
    filename = f"dumps/{caller}_{datetime.now().isoformat()}.json"
    with open(filename, "w") as f:
        json.dump(content, f)


def debug_dump_pickle(content: Union[dict, list], caller: str = "") -> None:
    filename = f"dumps/{caller}_{datetime.now().isoformat()}.pickle"
    with open(filename, "wb") as f:
        pickle.dump(content, f)


def dump_json_if_debug_enabled(content: Union[List, Dict]) -> None:
    caller_name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    if debug_dumps_enabled():
        debug_dump_json(content, caller=caller_name)


def dump_pickle_if_debug_enabled(content: Any) -> None:
    caller_name = inspect.getouterframes(inspect.currentframe(), 2)[1][3]
    if debug_dumps_enabled():
        debug_dump_pickle(content, caller=caller_name)


def move_file_to_download_folder(download: Download) -> None:
    """
    Moves the final product to the DOWNLOAD_FOLDER
    """
    input_file = f"{download.game_id}_ready.mkv"

    download_dir = get_download_folder()
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    tprint(f"Moving final to video to {download_dir}")
    output_file = f"{download_dir}/{download.game_info}.mkv"
    move(input_file, output_file)


def write_lines_to_file(lines: List[str], file_: str) -> None:
    with open(file_, "w") as f:
        f.writelines(lines)


def read_lines_from_file(file_: str) -> List[str]:
    with open(file_, "r") as f:
        return f.readlines()


def tprint(message: str, debug_only: bool = False) -> None:
    if debug_dumps_enabled() or not debug_only:
        print(f"{datetime.now().strftime('%b %-d %H:%M:%S')} - {message}")
