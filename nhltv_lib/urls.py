teams_url = "https://statsapi.web.nhl.com/api/v1/teams?"

schedule_url = (
    "http://statsapi.web.nhl.com/api/v1/schedule?"
    + "expand=schedule.teams,schedule.linescore,schedule"
    + ".scoringplays,schedule.game.content.media.epg&startDate="
)


def get_schedule_url_between_dates(start_date, end_date):
    return schedule_url + (
        start_date
        + "&endDate="
        + end_date
        + "&site=en_nhl&platform=playstation"
    )
