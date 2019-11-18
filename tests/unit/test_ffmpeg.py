import pytest
import itertools
from nhltv_lib.ffmpeg import (
    concat_video,
    cut_video,
    get_video_length,
    split_video_into_cuts,
    detect_silence,
    show_video_streams,
)


@pytest.fixture(scope="function", autouse=True)
def mock_call_subp_and_raise(mocker):
    return mocker.patch(
        "nhltv_lib.ffmpeg.call_subprocess_and_raise_on_error",
        return_value=[b"14401.1"],
    )


@pytest.fixture(scope="function", autouse=True)
def mock_call_subp_iter(mocker):
    return mocker.patch(
        "nhltv_lib.ffmpeg.call_subprocess_and_get_stdout_iterator",
        return_value=(None, (i for i in ["foo", "bar", "baz"])),
    )


def test_concat_video(mock_call_subp_and_raise):
    concat_video("conc.txt", "outp.mkv")
    command = (
        f"ffmpeg -y -nostats -loglevel 0 -f concat -safe 0 -i "
        f"conc.txt -c copy  outp.mkv"
    )
    mock_call_subp_and_raise.assert_called_once_with(command)


def test_concat_video_w_extraargs(mock_call_subp_and_raise):
    concat_video("conc.txt", "outp.mkv", extra_args="btree -c")
    command = (
        f"ffmpeg -y -nostats -loglevel 0 -f concat -safe 0 -i "
        f"conc.txt -c copy btree -c outp.mkv"
    )
    mock_call_subp_and_raise.assert_called_once_with(command)


def test_cut_video(mock_call_subp_and_raise):
    cut_video("input", "output", 10800)
    command = f"ffmpeg -ss 0 -i input -t 10800 -c copy output"
    mock_call_subp_and_raise.assert_called_once_with(command)


def test_show_video_streams(mock_call_subp_and_raise):
    a = show_video_streams("file")
    command = (
        f"ffprobe -i file -show_streams",
        f" -select_streams v -loglevel error",
    )
    mock_call_subp_and_raise.assert_called_once_with(command)
    assert a == [b"14401.1"]


def test_get_video_length(mock_call_subp_and_raise):
    assert get_video_length("input") == 14401
    command = (
        f"ffprobe -v error -show_entries format=duration -of "
        f"default=noprint_wrappers=1:nokey=1 input"
    )
    mock_call_subp_and_raise.assert_called_once_with(command)


def test_split_video_into_cuts(mock_call_subp_and_raise):
    split_video_into_cuts("foo", 3, 0, 1)
    command = f"ffmpeg -y -nostats -i foo -ss 0 "
    command += f"-c:v copy -c:a copy 3/cut1.mp4"

    mock_call_subp_and_raise.assert_called_once_with(command)


def test_split_video_into_cuts_w_end(mock_call_subp_and_raise):
    split_video_into_cuts("foo", 3, 0, 1, 400)
    command = f"ffmpeg -y -nostats -i foo -ss 0 -t 400 "
    command += f"-c:v copy -c:a copy 3/cut1.mp4"

    mock_call_subp_and_raise.assert_called_once_with(command)


def test_detect_silence(mocker, mock_call_subp_iter):
    mockiter = mocker.Mock(side_effect=["foo", "bar", "baz"])

    out = detect_silence("file")

    command = (
        f"ffmpeg -y -nostats -i file -af silencedetect=n=-50dB:d=10 "
        f"-c:v copy -c:a libmp3lame -f mp4 /dev/null"
    )
    mock_call_subp_iter.assert_called_once_with(command)

    for a, b in itertools.zip_longest(out, iter(mockiter, b"")):
        assert a == b
