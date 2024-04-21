NHLTV_BASE_API_URL = "https://nhltv.nhl.com/api"

TEAMS_URL = NHLTV_BASE_API_URL + "/v3/sso/nhl/teams"

SCHEDULE_URL = NHLTV_BASE_API_URL + "/v2/events?sort_direction=asc&date_time_from="

LOGIN_URL = NHLTV_BASE_API_URL + "/v3/sso/nhl/login"


def get_player_settings_url(feed_id: str) -> str:
    return NHLTV_BASE_API_URL + f"/v3/contents/{feed_id}/player-settings"


def get_schedule_url_between_dates(start_date: str, end_date: str) -> str:
    return SCHEDULE_URL + (
        start_date
        + "T00:00:00-04:00&date_time_to="
        + end_date
        + "T00:00:00-04:00"
    )


def get_session_key_url(player_settings: dict) -> str:
    return NHLTV_BASE_API_URL + f"/v3/contents/{player_settings["videoid"]}/check-access"


def get_stream_url(player_settings: dict) -> str:
    return player_settings["streamUrlProviderInfo"]["data"]["streamAccessUrl"]
