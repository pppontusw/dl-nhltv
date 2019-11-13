import time
from urllib.parse import quote_plus

TEAMS_URL = "https://statsapi.web.nhl.com/api/v1/teams?"

SCHEDULE_URL = (
    "http://statsapi.web.nhl.com/api/v1/schedule?"
    + "expand=schedule.teams,schedule.linescore,schedule"
    + ".scoringplays,schedule.game.content.media.epg&startDate="
)

TOKEN_URL = (
    "https://user.svc.nhl.com/oauth/token?grant_type=client_credentials"
)  # from https:/www.nhl.com/tv?affiliated=NHLTVLOGIN

LOGIN_URL = (
    "https://gateway.web.nhl.com/ws/subscription/flow/nhlPurchase.login"
)


def get_schedule_url_between_dates(start_date, end_date):
    return SCHEDULE_URL + (
        start_date
        + "&endDate="
        + end_date
        + "&site=en_nhl&platform=playstation"
    )


def get_referer(stream):
    return "https://www.nhl.com/tv/%s/%s/%s" % (
        stream.game_id,
        stream.event_id,
        stream.content_id,
    )


def get_session_key_url(event_id):
    epoch_time_now = str(int(round(time.time() * 1000)))

    return (
        "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?eventId="
        + str(event_id)
        + "&format=json&platform=WEB_MEDIAPLAYER&subject=NHLTV&_="
        + epoch_time_now
    )


def get_stream_url(content_id, session_key):
    # Org
    return (
        "https://mf.svc.nhl.com/ws/media/mf/v2.4/stream?contentId="
        + str(content_id)
        + "&playbackScenario=HTTP_CLOUD_TABLET_60&platform=IPAD&sessionKey="
        + quote_plus(session_key)
    )
