import os
import logging
import re
from glob import iglob
from nhltv_lib.common import print_progress_bar
from nhltv_lib.exceptions import ExternalProgramError
from nhltv_lib.process import (
    call_subprocess,
    call_subprocess_and_raise_on_error,
)

logger = logging.getLogger("nhltv")


def skip_silence(download):
    """
    Analyzes the video for silent parts and removes them
    """
    analyze_output = _start_analyzing_for_silence(download.game_id)

    marks = _create_marks_from_analyzed_output(analyze_output)

    seg = _create_segments(download.game_id, marks)

    concat_list = _create_concat_list(download.game_id, seg)
    _write_concat_list(download.game_id, concat_list)

    _merge_cuts_to_silent_video(download.game_id)

    _clean_up_cuts(download.game_id)


def _start_analyzing_for_silence(game_id):
    filename = f"{game_id}_raw.mkv"
    logger.debug("Analyzing " + filename + " for silence.")
    command = (
        "ffmpeg -y -nostats -i "
        + filename
        + " -af silencedetect=n=-50dB:d=10 -c:v copy -c:a libmp3lame -f"
        + " mp4 /dev/null"
    )
    p = call_subprocess(command)
    pi = iter(p.stdout.readline, b"")
    return pi


def _create_marks_from_analyzed_output(analyze_output):
    marks = ["0"]
    for line in analyze_output:
        line = line.decode()
        if "silencedetect" in line:
            start_match = re.search(
                r".*silence_start: (.*)", line, re.M | re.I
            )
            end_match = re.search(
                r".*silence_end: (.*) \|.*", line, re.M | re.I
            )
            if (start_match is not None) and (start_match.lastindex == 1):
                marks.append(start_match.group(1))

            if (end_match is not None) and end_match.lastindex == 1:
                marks.append(end_match.group(1))

    # If it is not an even number of segments then add the end point.
    # If the last silence goes
    # to the endpoint then it will be an even number.
    if len(marks) % 2 == 1:
        marks.append("end")
    return marks


def _create_segments(game_id, marks):
    filename = f"{game_id}_raw.mkv"
    logger.debug("Creating segments.")
    seg = 0
    # Create segments
    for i, mark in enumerate(marks):
        if i % 2 == 0:
            if marks[i + 1] != "end":
                seg = seg + 1
                length = float(marks[i + 1]) - float(mark)
                command = (
                    "ffmpeg -y -nostats -i "
                    + filename
                    + " -ss "
                    + str(mark)
                    + " -t "
                    + str(length)
                    + " -c:v copy -c:a copy "
                    + str(game_id)
                    + "/cut"
                    + str(seg)
                    + ".mp4"
                )
            else:
                seg = seg + 1
                command = (
                    "ffmpeg -y -nostats -i "
                    + filename
                    + " -ss "
                    + str(mark)
                    + " -c:v copy -c:a copy "
                    + str(game_id)
                    + "/cut"
                    + str(seg)
                    + ".mp4"
                )
            call_subprocess_and_raise_on_error(command)
            print_progress_bar(seg, len(marks), prefix="Creating segments:")
    return seg


def _create_concat_list(game_id, seg):
    # Create file list
    content = []
    for i in range(1, seg + 1):
        # if some cut doesn't contain a video stream,
        # it will break the output file
        command = (
            f"ffprobe -i {game_id}/cut{i}.mp4 -show_streams",
            f" -select_streams v -loglevel error",
        )
        p = call_subprocess(command)
        p.wait()
        if p.returncode != 0:
            raise ExternalProgramError(p.stdout.readlines())
        if p.stdout.readlines() != []:
            content.append("file\t" + "cut" + str(i) + ".mp4\n")
    return content


def _write_concat_list(game_id, content):
    with open(f"{game_id}/concat_list.txt", "w") as f:
        f.writelines(content)


def _merge_cuts_to_silent_video(game_id):
    command = (
        f"ffmpeg -y -nostats -f concat -i "
        f"{game_id}/concat_list.txt -c "
        f"copy {game_id}_silent.mkv"
    )
    logger.debug(
        "Merging segments back to single video and saving: "
        + f"{game_id}_silent.mkv"
    )
    call_subprocess_and_raise_on_error(command)


def _clean_up_cuts(game_id):
    for path in iglob(os.path.join(str(game_id), "cut*.mp4")):
        os.remove(path)
