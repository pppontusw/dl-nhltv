from nhltv_lib.stream import (
    get_shorten_video,
    stream_matches_home_away,
    create_stream_object,
    is_ready_to_download,
    get_best_stream,
    create_stream_objects,
    get_streams_to_download,
    NHLStream,
)
from nhltv_lib.game import Game


def test_stream_matches_home_away():
    assert stream_matches_home_away(Game(123, "1 vs 2", True, []), "HOME")
    assert not stream_matches_home_away(Game(123, "1 vs 2", False, []), "HOME")
    assert not stream_matches_home_away(Game(123, "1 vs 2", True, []), "AWAY")
    assert stream_matches_home_away(Game(123, "1 vs 2", False, []), "AWAY")


def test_get_streams_to_download(mocker):
    mocker.patch("nhltv_lib.stream.filter")
    mocker.patch(
        "nhltv_lib.stream.create_stream_objects",
        return_value=[NHLStream(0, 0, 0)],
    )

    assert get_streams_to_download(Game(1, "", 2, 3)) == [NHLStream(0, 0, 0)]
