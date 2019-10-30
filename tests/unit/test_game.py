from datetime import datetime, timedelta
import pytest
from nhltv_lib.game import (
    get_days_back,
    get_checkinterval,
    get_next_game,
    get_start_date,
    get_end_date,
    check_if_game_involves_team,
    filter_games_with_team,
    fetch_games,
)


def test_get_days_back(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert get_days_back() == 2


def test_get_checkinterval(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert get_checkinterval() == 10


def test_get_next_game(mocker):
    mocked_start_date = mocker.patch("nhltv_lib.game.get_start_date")
    mocked_end_date = mocker.patch("nhltv_lib.game.get_end_date")
    mocked_fetch_games = mocker.patch("nhltv_lib.game.fetch_games")
    mocked_games_with_team = mocker.patch(
        "nhltv_lib.game.filter_games_with_team"
    )
    get_next_game()
    mocked_start_date.assert_called_once()
    mocked_end_date.assert_called_once()
    mocked_fetch_games.assert_called_once()
    mocked_games_with_team.assert_called_once()


@pytest.mark.parametrize("days", [1, 3, 6, -1])
def test_get_start_date(mocker, days):
    mocker.patch("nhltv_lib.game.get_days_back", return_value=days)
    assert (
        get_start_date()
        == (datetime.now().date() - timedelta(days=days)).isoformat()
    )


def test_get_end_date():
    assert get_end_date() == datetime.now().date().isoformat()


def test_filter_games_with_team(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_involves_team", return_value=True
    )

    assert len(filter_games_with_team(games_data)) == 17


def test_filter_games_with_team_no_game(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_involves_team", return_value=False
    )

    assert len(filter_games_with_team(games_data)) == 0


def test_check_if_game_involves_team(mocker):
    mocker.patch("nhltv_lib.game.get_team_id", return_value=18)
    yes = dict(
        teams=dict(home=dict(team=dict(id=18)), away=dict(team=dict(id=7)))
    )
    also_yes = dict(
        teams=dict(home=dict(team=dict(id=8)), away=dict(team=dict(id=18)))
    )
    no = dict(
        teams=dict(home=dict(team=dict(id=19)), away=dict(team=dict(id=7)))
    )

    assert check_if_game_involves_team(yes)
    assert check_if_game_involves_team(also_yes)
    assert not check_if_game_involves_team(no)


def test_fetch_games(mocker):
    mock_req_get = mocker.patch("requests.get")
    fetch_games("url")
    mock_req_get.assert_called_with("url")
