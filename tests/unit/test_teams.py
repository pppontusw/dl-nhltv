from nhltv_lib.teams import (
    get_team,
    find_team_by_id,
    fetch_teams,
    find_team_by_name,
    find_team_by_abbreviation,
)
from nhltv_lib.urls import TEAMS_URL


def test_fetch_teams(mocker):
    mock_req_get = mocker.patch("requests.get")
    fetch_teams()
    mock_req_get.assert_called_with(TEAMS_URL)


def test_find_team_by_id():
    assert get_team(18) == 18
    assert find_team_by_id(18) == 18


def test_find_team_by_name():
    assert get_team("Nashville Predators") == 18
    assert find_team_by_name("Nashville Predators") == 18
    assert get_team("Vegas Golden Knights") == 54
    assert find_team_by_name("Vegas Golden Knights") == 54


def test_find_team_by_abbreviation():
    assert get_team("NSH") == 18
    assert get_team("VGK") == 54
    assert find_team_by_abbreviation("NSH") == 18
    assert find_team_by_abbreviation("VGK") == 54
