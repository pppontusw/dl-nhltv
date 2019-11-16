import os

from nhltv_lib.common import move_file_to_download_folder
from nhltv_lib.process import call_subprocess_and_raise_on_error


def obfuscate(download):
    """
    Pads the end of the video with 100 minutes of black
    """
    inputFile = f"{download.game_id}_silent.mkv"
    black = os.path.join(os.path.dirname(__file__), "extras/black.mkv")
    fh = open(f"{download.game_id}/obfuscate_concat_list.txt", "w")
    fh.write("file\t" + inputFile + "\n")
    for _ in range(100):
        fh.write("file\t" + black + "\n")
    fh.close()
    outputFile = f"{download.game_id}_obfuscated.mkv"
    command = (
        f"ffmpeg -y -nostats -f concat -safe 0 -i "
        f"{download.game_id}/obfuscate_concat_list.txt "
        f"-c copy {outputFile}"
    )
    call_subprocess_and_raise_on_error(command)
    os.remove(inputFile)

    cut_to_closest_hour(download.game_id)

    move_file_to_download_folder(download)


def cut_to_closest_hour(game_id):
    """
    Cuts video to the closest hour, rounding down, minimum 1
    """
    inputFile = f"{game_id}_obfuscated.mkv"
    outputFile = f"{game_id}_ready.mkv"
    command = (
        "ffprobe -v error -show_entries format=duration -of \
                default=noprint_wrappers=1:nokey=1 %s"
        % inputFile
    )
    proc_out = call_subprocess_and_raise_on_error(command)
    length = proc_out[0]
    length = int(length.split(b".")[0])
    len_in_hours = length / 3600
    desired_len_in_seconds = (
        int(len_in_hours) * 3600 if int(len_in_hours) > 0 else 3600
    )
    command = "ffmpeg -ss 0 -i %s -t %d -c copy %s" % (
        inputFile,
        desired_len_in_seconds,
        outputFile,
    )
    call_subprocess_and_raise_on_error(command)
    os.remove(inputFile)
