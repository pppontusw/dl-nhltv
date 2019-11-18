import os
import logging

from nhltv_lib.common import move_file_to_download_folder, write_lines_to_file
from nhltv_lib.ffmpeg import cut_video, get_video_length, concat_video

logger = logging.getLogger("nhltv")


def obfuscate(download):
    """
    Pads the end of the video with 100 minutes of black
    """
    input_file = f"{download.game_id}_silent.mkv"

    obfuscate_concat_content = _create_obfuscation_concat_content(input_file)
    concat_list_file = f"{download.game_id}/obfuscate_concat_list.txt"

    write_lines_to_file(obfuscate_concat_content, concat_list_file)

    logger.debug("Obfuscating end time of video..")
    output_file = f"{download.game_id}_obfuscated.mkv"
    concat_video(concat_list_file, output_file)

    os.remove(input_file)

    cut_to_closest_hour(download.game_id)

    move_file_to_download_folder(download)


def _create_obfuscation_concat_content(input_file):
    black = os.path.join(os.path.dirname(__file__), "extras/black.mkv")
    content = []
    content.append("file\t" + f"../{input_file}" + "\n")
    for _ in range(100):
        content.append("file\t" + black + "\n")
    return content


def cut_to_closest_hour(game_id):
    """
    Cuts video to the closest hour, rounding down, minimum 1
    """
    input_file = f"{game_id}_obfuscated.mkv"

    video_length = get_video_length(input_file)

    desired_len_in_seconds = _get_desired_length_after_obfuscation(
        video_length
    )

    logger.debug("Cutting video to closest hour")
    output_file = f"{game_id}_ready.mkv"

    cut_video(input_file, output_file, desired_len_in_seconds)

    os.remove(input_file)


def _get_desired_length_after_obfuscation(length):
    """
    Gets the closest hour in seconds without cutting
    any of the actual video content
    """
    len_in_hours = length / 3600
    desired_len_in_seconds = (
        int(len_in_hours) * 3600 if int(len_in_hours) > 0 else 3600
    )
    return desired_len_in_seconds
