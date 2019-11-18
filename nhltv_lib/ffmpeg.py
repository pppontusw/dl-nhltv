from nhltv_lib.process import (
    call_subprocess_and_raise_on_error,
    call_subprocess_and_get_stdout_iterator,
)


def concat_video(concat_list_path, output_file, extra_args=""):
    command = (
        f"ffmpeg -y -nostats -loglevel 0 -f concat -safe 0 -i "
        f"{concat_list_path} -c copy {extra_args} {output_file}"
    )
    call_subprocess_and_raise_on_error(command)


def cut_video(input_file, output_file, length):
    command = (
        f"ffmpeg -ss 0 -i {input_file} -t {length} " f"-c copy {output_file}"
    )
    call_subprocess_and_raise_on_error(command)


def get_video_length(input_file):

    command = (
        f"ffprobe -v error -show_entries format=duration -of "
        f"default=noprint_wrappers=1:nokey=1 {input_file}"
    )

    proc_out = call_subprocess_and_raise_on_error(command)
    return int(proc_out[0].split(b".")[0])


def split_video_into_cuts(input_file, game_id, mark, seg, end=None):
    command = f"ffmpeg -y -nostats -i {input_file} -ss {mark} "
    if end:
        command += f"-t {end} "
    command += f"-c:v copy -c:a copy {game_id}/cut{seg}.mp4"
    call_subprocess_and_raise_on_error(command)


def show_video_streams(input_file):
    command = (
        f"ffprobe -i {input_file} -show_streams",
        f" -select_streams v -loglevel error",
    )
    proc_out = call_subprocess_and_raise_on_error(command)
    return proc_out


def detect_silence(input_file):
    """
    Runs silencedetect and returns an iterator over ffmpeg stdout
    """
    command = (
        f"ffmpeg -y -nostats -i {input_file} -af silencedetect=n=-50dB:d=10 "
        f"-c:v copy -c:a libmp3lame -f mp4 /dev/null"
    )

    _, pi = call_subprocess_and_get_stdout_iterator(command)
    return pi
