from nhltv_lib.skip_silence import (
    _create_marks_from_analyzed_output,
    _create_segments,
    _start_analyzing_for_silence,
    _merge_cuts_to_silent_video,
    _remove_raw_file,
    _create_concat_list,
    _clean_up_cuts,
)


def test_create_marks(fake_silencedetect_output):
    assert _create_marks_from_analyzed_output(fake_silencedetect_output) == [
        "0",
        "258.047",
        "409.219",
        "1356.19",
        "1452.06",
        "1982.71",
        "2074.94",
        "2263.41",
        "2355.84",
        "2961.15",
        "3093.69",
        "3212.44",
        "3364.34",
        "3510.38",
        "3699.52",
        "3809.82",
        "3965.78",
        "4707.25",
        "4805.85",
        "5053.37",
        "5148.24",
        "5719.03",
        "5811.88",
        "6306.4",
        "6468.18",
        "6468.78",
        "6503.43",
        "6578.89",
        "6730.9",
        "6813.8",
        "6968.4",
        "7129.52",
        "7313.41",
        "7921.87",
        "7990.91",
        "8392.66",
        "8485.86",
        "9005.57",
        "9099.82",
        "9621.25",
        "9761.74",
        "end",
    ]


def test_create_segments(mocker):
    marks = ["0", "258.047", "409.219", "end"]
    call = mocker.call
    mocker.patch("nhltv_lib.skip_silence.print_progress_bar")
    m = mocker.patch("nhltv_lib.skip_silence.split_video_into_cuts")
    _create_segments(1, marks)
    calls = [
        call("1_raw.mkv", 1, "0", 1, 258.047),
        call("1_raw.mkv", 1, "409.219", 2),
    ]
    m.assert_has_calls(calls)


def test_start_analyzing_for_silence(mocker):
    mo = mocker.patch("nhltv_lib.skip_silence.detect_silence")
    _start_analyzing_for_silence(30)
    mo.assert_called_once_with("30_raw.mkv")


def test_remove_raw_file(mocker):
    mock = mocker.patch("os.remove")
    _remove_raw_file(30)
    mock.assert_called_once_with("30_raw.mkv")


def test_create_concat_list(mocker):
    mocker.patch(
        "nhltv_lib.skip_silence.show_video_streams",
        side_effect=[["foo"], ["bar"], ["baz"]],
    )
    assert _create_concat_list(30, 3) == [
        "file\tcut1.mp4\n",
        "file\tcut2.mp4\n",
        "file\tcut3.mp4\n",
    ]


def test_create_concat_list_w_missing_stream(mocker):
    mocker.patch(
        "nhltv_lib.skip_silence.show_video_streams",
        side_effect=[["foo"], [], ["baz"]],
    )
    assert _create_concat_list(30, 3) == [
        "file\tcut1.mp4\n",
        "file\tcut3.mp4\n",
    ]


def test_clean_up_cuts(mocker):
    call = mocker.call
    mocker.patch("nhltv_lib.skip_silence.iglob", return_value=["foo", "bar"])
    mock_osrm = mocker.patch("os.remove")
    _clean_up_cuts(3)
    calls = [call("foo"), call("bar")]
    mock_osrm.assert_has_calls(calls)


def test_merge_cuts_to_silent(mocker):
    mo = mocker.patch("nhltv_lib.skip_silence.concat_video")
    _merge_cuts_to_silent_video(30)
    mo.assert_called_once_with("30/concat_list.txt", "30_silent.mkv")
