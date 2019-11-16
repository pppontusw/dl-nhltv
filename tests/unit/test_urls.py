import time
from nhltv_lib.urls import (
    get_referer,
    get_stream_url,
    get_session_key_url,
    get_schedule_url_between_dates,
    SCHEDULE_URL,
)


def test_get_schedule_url_btwn_dates():
    assert get_schedule_url_between_dates(
        "2222-22-22", "3333-33-33"
    ) == SCHEDULE_URL + (
        "2222-22-22"
        + "&endDate="
        + "3333-33-33"
        + "&site=en_nhl&platform=playstation"
    )


def test_get_referer(fake_streams):
    assert (
        get_referer(fake_streams[0])
        == "https://www.nhl.com/tv/2019020104/221-2003475/69517903"
    )


def test_get_session_key_url(mocker):
    t = time.time()
    mocker.patch("time.time", return_value=t)
    assert get_session_key_url(2019020104) == (
        "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId=2019020104"
        + "&format=json&platform=WEB_MEDIAPLAYER&subject=NHLTV&_="
        + str(int(round(t * 1000)))
    )


def test_get_stream_url():
    assert get_stream_url(400, "bar") == (
        "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId=400"
        + "&playbackScenario=HTTP_CLOUD_TABLET_60&platform=IPAD&sessionKey=bar"
    )
