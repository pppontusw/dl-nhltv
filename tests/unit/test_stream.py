from nhltv_lib.stream import (
    get_quality,
    get_shorten_video,
    stream_matches_home_away,
    create_stream_object,
    is_ready_to_download,
    get_best_stream,
    create_stream_objects,
    get_streams_to_download,
    Stream,
    get_preferred_streams,
)
from nhltv_lib.game import Game


def test_stream_matches_home_away():
    assert stream_matches_home_away(Game(123, True, []), "HOME")
    assert not stream_matches_home_away(Game(123, False, []), "HOME")
    assert not stream_matches_home_away(Game(123, True, []), "AWAY")
    assert stream_matches_home_away(Game(123, False, []), "AWAY")


def test_create_stream_object(mocker):
    mocker.patch(
        "nhltv_lib.stream.get_best_stream",
        return_value={"mediaPlaybackId": 123, "eventId": 456},
    )
    strmobj = create_stream_object(Game(000, False, []))
    assert strmobj.game_id == 000
    assert strmobj.content_id == 123
    assert strmobj.event_id == 456


def test_is_ready_to_download():
    assert is_ready_to_download(
        Game(
            0,
            False,
            [
                dict(
                    mediaState="MEDIA_ARCHIVE",
                    language="fra",
                    mediaFeedType="AWAY",
                )
            ],
        )
    )
    assert not is_ready_to_download(
        Game(
            0,
            False,
            [
                dict(
                    mediaState="MEDIA_ON", language="fra", mediaFeedType="AWAY"
                )
            ],
        )
    )


def test_create_stream_objects(mocker):
    mockfunc = mocker.patch(
        "nhltv_lib.stream.create_stream_object", return_value=True
    )
    assert isinstance(create_stream_objects([0]), map)

    # tuple call exhausts iterator which makes the call to mockfunc
    tuple(create_stream_objects([0]))
    mockfunc.assert_called_once_with(0)


def test_get_best_stream():
    streams = [
        dict(mediaState="MEDIA_ARCHIVE", language="fra", mediaFeedType="AWAY"),
        dict(mediaState="MEDIA_ARCHIVE", language="eng", mediaFeedType="AWAY"),
        dict(mediaState="MEDIA_ARCHIVE", language="fra", mediaFeedType="HOME"),
        dict(mediaState="MEDIA_ARCHIVE", language="eng", mediaFeedType="HOME"),
    ]

    assert get_best_stream(Game(1, True, streams)) == streams[3]
    assert get_best_stream(Game(1, False, streams)) == streams[1]


def test_get_best_stream_w_preferred_stream(mocker):
    mocker.patch(
        "nhltv_lib.stream.get_preferred_streams", return_value=["CBS"]
    )
    streams = [
        dict(
            mediaState="MEDIA_ARCHIVE",
            language="fra",
            mediaFeedType="AWAY",
            callLetters="CBS",
        ),
        dict(mediaState="MEDIA_ARCHIVE", language="eng", mediaFeedType="AWAY"),
        dict(mediaState="MEDIA_ARCHIVE", language="fra", mediaFeedType="HOME"),
        dict(mediaState="MEDIA_ARCHIVE", language="eng", mediaFeedType="HOME"),
    ]

    assert get_best_stream(Game(1, True, streams)) == streams[0]


def test_get_streams_to_download(mocker):
    mocker.patch("nhltv_lib.stream.filter")
    mocker.patch(
        "nhltv_lib.stream.create_stream_objects",
        return_value=[Stream(0, 0, 0)],
    )

    assert get_streams_to_download(Game(1, 2, 3)) == [Stream(0, 0, 0)]


def test_get_quality():
    assert get_quality() == 3333


def test_get_shorten_video():
    assert not get_shorten_video()


def test_get_preferred_stream():
    assert get_preferred_streams() == ["FS-TN"]


def test_get_preferred_stream_list(
    mocker, mocked_parse_args, parsed_args, parsed_args_list
):
    parsed_args_list[10] = ["FS-TN", "CBS"]
    mocked_parse_args.return_value = parsed_args(*parsed_args_list)
    assert get_preferred_streams() == ["FS-TN", "CBS"]


def test_get_preferred_stream_none(
    mocker, mocked_parse_args, parsed_args, parsed_args_list
):
    parsed_args_list[10] = None
    mocked_parse_args.return_value = parsed_args(*parsed_args_list)
    assert get_preferred_streams() == []


def test_get_shorten_video_yes(
    mocker, mocked_parse_args, parsed_args, parsed_args_list
):
    parsed_args_list[8] = True
    mocked_parse_args.return_value = parsed_args(*parsed_args_list)
    assert get_shorten_video()


def test_get_quality_none(
    mocker, mocked_parse_args, parsed_args, parsed_args_list
):
    parsed_args_list[3] = None
    mocked_parse_args.return_value = parsed_args(*parsed_args_list)
    assert get_quality() == 5000
