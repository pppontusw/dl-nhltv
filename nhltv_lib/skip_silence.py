from typing import Iterable, List, Optional, Match
import os
import re
from glob import iglob
from nhltv_lib.common import print_progress_bar, write_lines_to_file, tprint
from nhltv_lib.ffmpeg import (
    split_video_into_cuts,
    concat_video,
    show_video_streams,
    detect_silence,
)
from nhltv_lib.types import Download


def skip_silence(download: Download) -> None:
    """
    Analyzes the video for silent parts and removes them
    """
    analyze_output = _start_analyzing_for_silence(download.game_id)

    marks = _create_marks_from_analyzed_output(analyze_output)

    seg = _create_segments(download.game_id, marks)

    _remove_raw_file(download.game_id)

    concat_list = _create_concat_list(download.game_id, seg)
    write_lines_to_file(concat_list, f"{download.game_id}/concat_list.txt")

    _merge_cuts_to_silent_video(download.game_id)

    _clean_up_cuts(download.game_id)


def _start_analyzing_for_silence(game_id: int) -> Iterable[bytes]:
    filename = f"{game_id}_raw.mkv"
    tprint(f"Analyzing video for silence..")
    return detect_silence(filename)


def _create_marks_from_analyzed_output(
    analyze_output: Iterable[bytes]
) -> List[str]:
    marks: List[str] = ["0"]
    for line in analyze_output:
        decoded_line: str = line.decode()
        if "silencedetect" in decoded_line:
            start_match: Optional[Match] = re.search(
                r".*silence_start: (.*)", decoded_line, re.M | re.I
            )
            end_match: Optional[Match] = re.search(
                r".*silence_end: (.*) \|.*", decoded_line, re.M | re.I
            )
            if (start_match is not None) and (start_match.lastindex == 1):
                start: str = start_match.group(1)
                marks.append(start)

            if (end_match is not None) and end_match.lastindex == 1:
                end: str = end_match.group(1)
                marks.append(end)

    # If it is not an even number of segments then add the end point.
    # If the last silence goes
    # to the endpoint then it will be an even number.
    if len(marks) % 2 == 1:
        marks.append("end")
    return marks


def _create_segments(game_id: int, marks: List[str]) -> int:
    filename: str = f"{game_id}_raw.mkv"
    tprint("Creating segments", debug_only=True)
    seg: int = 0
    for i, mark in enumerate(marks):
        if i % 2 == 0:
            if marks[i + 1] != "end":
                seg = seg + 1
                length = float(marks[i + 1]) - float(mark)
                split_video_into_cuts(filename, game_id, mark, seg, length)
            else:
                seg = seg + 1
                split_video_into_cuts(filename, game_id, mark, seg)
            print_progress_bar(seg, len(marks), prefix="Creating segments:")
    return seg


def _remove_raw_file(game_id: int) -> None:
    os.remove(f"{game_id}_raw.mkv")


def _create_concat_list(game_id: int, seg: int) -> List[str]:
    content: List[str] = []
    for i in range(1, seg + 1):
        # if some cut doesn't contain a video stream,
        # it will break the output file
        streams = show_video_streams(f"{game_id}/cut{i}.mp4")
        if streams != []:
            content.append("file\t" + "cut" + str(i) + ".mp4\n")
    return content


def _merge_cuts_to_silent_video(game_id: int) -> None:
    tprint(
        "Merging segments back to single video and saving: "
        + f"{game_id}_silent.mkv",
        debug_only=True,
    )
    concat_video(f"{game_id}/concat_list.txt", f"{game_id}_silent.mkv")


def _clean_up_cuts(game_id: int) -> None:
    for path in iglob(os.path.join(str(game_id), "cut*.mp4")):
        os.remove(path)
