from nhltv_lib.skip_silence import (
    _create_marks_from_analyzed_output,
    _create_segments,
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


def test_create_segmenst(mocker):
    marks = ["0", "258.047", "409.219", "end"]
    call = mocker.call
    mocker.patch("nhltv_lib.skip_silence.print_progress_bar")
    m = mocker.patch(
        "nhltv_lib.skip_silence.call_subprocess_and_raise_on_error"
    )
    _create_segments(1, marks)
    calls = [
        call(
            "ffmpeg -y -nostats -i 1_raw.mkv -ss 0 -t 258.047 -c:v copy -c:a copy 1/cut1.mp4"  # noqa: E501
        ),
        call(
            "ffmpeg -y -nostats -i 1_raw.mkv -ss 409.219 -c:v copy -c:a copy 1/cut2.mp4"  # noqa: E501
        ),
    ]
    m.assert_has_calls(calls)
