from datetime import datetime, timedelta
import pytest
from nhltv_lib.game import (
    get_days_back,
    filter_games_on_blackout_waitlist,
    get_checkinterval,
    get_games_to_download,
    get_start_date,
    get_end_date,
    check_if_game_involves_team,
    filter_games_with_team,
    fetch_games,
    filter_duplicates,
    filter_games_already_downloaded,
    check_if_game_is_downloaded,
    create_game_object,
    create_game_objects,
    is_home_game,
    filter_games_on_archive_waitlist,
    get_team_id,
    filter_games,
    filter_games_that_have_not_started,
)


def test_filter_games(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_is_downloaded", return_value=True
    )
    mocker.patch("nhltv_lib.game.get_archive_wait_list", return_value={})
    mocker.patch("nhltv_lib.game.get_blackout_wait_list", return_value={})
    mocker.patch("nhltv_lib.game.get_team_id", return_value=18)
    filter_games(games_data) == games_data["dates"][1]["games"][6]


def test_filter_games_not_started(mocker, fake_games):
    da = datetime.now()
    mock_time = mocker.patch("nhltv_lib.game.datetime")
    mock_time.now.return_value = da - timedelta(minutes=30)
    mock_time.fromisoformat.return_value = da
    filter_games_that_have_not_started(fake_games) == []


def test_get_days_back(mocker, parsed_arguments):
    mocker.patch("nhltv_lib.game.get_arguments", return_value=parsed_arguments)
    assert get_days_back() == 2


@pytest.mark.parametrize(
    "team", [("VGK", 54), ("NSH", 18), ("DET", 17), ("MTL", 8)]
)
def test_get_team_id_other(mocker, parsed_args_list, parsed_args, team):
    parsed_args_list[0] = team[0]
    parsed_arguments = parsed_args(*parsed_args_list)
    mocker.patch("nhltv_lib.game.get_arguments", return_value=parsed_arguments)
    assert get_team_id() == team[1]


def test_get_checkinterval(mocker, parsed_arguments):
    mocker.patch("nhltv_lib.game.get_arguments", return_value=parsed_arguments)
    assert get_checkinterval() == 10


def test_get_checkinterval_non_int(mocker, parsed_args_list, parsed_args):
    parsed_args_list[5] = None
    parsed_arguments = parsed_args(*parsed_args_list)
    mocker.patch("nhltv_lib.game.get_arguments", return_value=parsed_arguments)
    assert get_checkinterval() == 10


def test_get_days_back_non_int(mocker, parsed_args_list, parsed_args):
    parsed_args_list[7] = None
    parsed_arguments = parsed_args(*parsed_args_list)
    mocker.patch("nhltv_lib.game.get_arguments", return_value=parsed_arguments)
    assert get_days_back() == 3


def test_get_games_to_download(mocker, fake_game_objects):
    mocked_start_date = mocker.patch("nhltv_lib.game.get_start_date")
    mocked_end_date = mocker.patch("nhltv_lib.game.get_end_date")
    mocked_fetch_games = mocker.patch("nhltv_lib.game.fetch_games")
    mocked_games_downloaded = mocker.patch("nhltv_lib.game.filter_games")
    mocker.patch(
        "nhltv_lib.game.create_game_objects", return_value=fake_game_objects
    )
    games = get_games_to_download()
    mocked_start_date.assert_called_once()
    mocked_end_date.assert_called_once()
    mocked_fetch_games.assert_called_once()
    mocked_games_downloaded.assert_called_once()
    assert games == fake_game_objects


@pytest.mark.parametrize("days", [1, 3, 6, -1])
def test_get_start_date(mocker, days):
    mocker.patch("nhltv_lib.game.get_days_back", return_value=days)
    assert (
        get_start_date()
        == (datetime.now().date() - timedelta(days=days)).isoformat()
    )


def test_get_end_date():
    assert get_end_date() == datetime.now().date().isoformat()


def test_filter_games_already_downloaded(mocker):
    mocker.patch(
        "nhltv_lib.game.check_if_game_is_downloaded", return_value=True
    )
    assert len(list(filter_games_already_downloaded(({}, {})))) == 2
    assert isinstance(filter_games_already_downloaded(({}, {})), filter)


def test_check_if_game_is_downloaded(mocker):
    mocker.patch("nhltv_lib.game.get_downloaded_games", return_value=[1])
    assert check_if_game_is_downloaded({"gamePk": 2})


def test_check_if_game_is_downloaded_neg(mocker):
    mocker.patch("nhltv_lib.game.get_downloaded_games", return_value=[1])
    assert not check_if_game_is_downloaded({"gamePk": 1})


def test_filter_games_with_team(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_involves_team", return_value=True
    )

    assert len(filter_games_with_team(games_data)) == 17
    assert isinstance(filter_games_with_team(games_data), tuple)


def test_filter_games_with_team_no_game(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_involves_team", return_value=False
    )

    assert len(filter_games_with_team(games_data)) == 0
    assert isinstance(filter_games_with_team(games_data), tuple)


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


def test_filter_duplicates():
    yes = ({"gamePk": 1}, {"gamePk": 2})
    no = ({"gamePk": 1}, {"gamePk": 1})

    assert filter_duplicates(yes) == yes
    assert filter_duplicates(no) != no
    assert len(filter_duplicates(no)) == 1
    assert isinstance(filter_duplicates(yes), tuple)


def test_create_game_objects(mocker):
    mocked_game_obj = mocker.patch("nhltv_lib.game.create_game_object")
    assert isinstance(create_game_objects(("boo",)), map)

    # tuple call exhausts the generator which calls the mocked func
    tuple(create_game_objects(("boo",)))
    mocked_game_obj.assert_called_once_with("boo")


def test_create_game_object(mocker, games_data):
    igame = games_data["dates"][0]["games"][0]
    mocker.patch("nhltv_lib.game.is_home_game", return_value=True)
    game = create_game_object(igame)
    assert game.game_id == igame["gamePk"]
    assert game.is_home_game is True
    assert game.streams == igame["content"]["media"]["epg"][0]["items"]


def test_create_game_object_away(mocker, games_data):
    igame = games_data["dates"][1]["games"][1]
    mocker.patch("nhltv_lib.game.is_home_game", return_value=False)
    game = create_game_object(igame)
    assert game.game_id == igame["gamePk"]
    assert game.is_home_game is False
    assert game.streams == igame["content"]["media"]["epg"][0]["items"]


def test_is_home_game(mocker):
    mocker.patch("nhltv_lib.game.get_team_id", return_value=18)
    assert is_home_game(dict(teams=dict(home=dict(team=dict(id=18)))))
    assert not is_home_game(dict(teams=dict(home=dict(team=dict(id=19)))))


def test_filter_games_on_archive_waitlist(mocker):
    mocker.patch(
        "nhltv_lib.game.get_archive_wait_list", return_value={"2": 0, "3": 0}
    )

    assert list(
        filter_games_on_archive_waitlist([{"gamePk": 3}, {"gamePk": 4}])
    ) == [{"gamePk": 4}]


def test_filter_games_on_blackout_waitlist(mocker):
    mocker.patch(
        "nhltv_lib.game.get_blackout_wait_list", return_value={"2": 0, "3": 0}
    )

    assert list(
        filter_games_on_blackout_waitlist([{"gamePk": 3}, {"gamePk": 4}])
    ) == [{"gamePk": 4}]
