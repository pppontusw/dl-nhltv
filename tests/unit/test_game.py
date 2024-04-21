from datetime import datetime, timedelta
import pytest
from nhltv_lib.game import (
    check_if_game_involves_team,
    get_days_back,
    get_checkinterval,
    get_games_to_download,
    get_start_date,
    get_end_date,
    filter_games_with_team,
    filter_duplicates,
    create_game_objects,
    filter_games,
    filter_games_that_have_not_started,
    get_team_id,
)


@pytest.fixture
def mock_get_args(mocker):
    return mocker.patch("nhltv_lib.game.get_arguments")


@pytest.fixture
def mock_get_team_id(mocker):
    return mocker.patch("nhltv_lib.game.get_team_id", return_value=18)


def test_filter_games(mocker, games_data):
    filter_games(games_data) == games_data["data"][5]


def test_filter_games_not_started(mocker, fake_games):
    da = datetime.now()
    mock_time = mocker.patch("nhltv_lib.game.datetime")
    mock_time.now.return_value = da - timedelta(minutes=30)
    mock_time.fromisoformat.return_value = da
    filter_games_that_have_not_started(fake_games) == []


def test_get_days_back(mocker, parsed_arguments, mock_get_args):
    mock_get_args.return_value = parsed_arguments
    assert get_days_back() == 2


@pytest.mark.parametrize(
    "team", [("VGK", 54), ("NSH", 18), ("DET", 17), ("MTL", 8)]
)
def test_get_team_id_other(
    mocker, parsed_args_list, parsed_args, team, mock_get_args
):
    parsed_args_list[0] = team[0]
    parsed_arguments = parsed_args(*parsed_args_list)
    mock_get_args.return_value = parsed_arguments
    assert get_team_id() == team[1]


def test_get_checkinterval(mocker, parsed_arguments, mock_get_args):
    mock_get_args.return_value = parsed_arguments
    assert get_checkinterval() == 10


def test_get_checkinterval_non_int(
    mocker, parsed_args_list, parsed_args, mock_get_args
):
    parsed_args_list[5] = None
    parsed_arguments = parsed_args(*parsed_args_list)
    mock_get_args.return_value = parsed_arguments
    assert get_checkinterval() == 10


def test_get_days_back_non_int(
    mocker, parsed_args_list, parsed_args, mock_get_args
):
    parsed_args_list[6] = None
    parsed_arguments = parsed_args(*parsed_args_list)
    mock_get_args.return_value = parsed_arguments
    assert get_days_back() == 3


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

    assert len(filter_games_with_team(games_data)) == 8
    assert isinstance(filter_games_with_team(games_data), tuple)


def test_filter_games_with_team_no_game(mocker, games_data):
    mocker.patch(
        "nhltv_lib.game.check_if_game_involves_team", return_value=False
    )

    assert len(filter_games_with_team(games_data)) == 0
    assert isinstance(filter_games_with_team(games_data), tuple)


# TODO fix
# def test_check_if_game_involves_team(mocker, mock_get_team_id):
# yes = dict(
# teams=dict(home=dict(team=dict(id=18)), away=dict(team=dict(id=7)))
# )
# also_yes = dict(
# teams=dict(home=dict(team=dict(id=8)), away=dict(team=dict(id=18)))
# )
# no = dict(
# teams=dict(home=dict(team=dict(id=19)), away=dict(team=dict(id=7)))
# )

# assert check_if_game_involves_team(yes)
# assert check_if_game_involves_team(also_yes)
# assert not check_if_game_involves_team(no)


def test_filter_duplicates():
    yes = ({"id": 1}, {"id": 2})
    no = ({"id": 1}, {"id": 1})

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


# TODO fix
# def test_create_game_object(mocker, games_data):
# igame = games_data["dates"][0]["games"][0]
# mocker.patch("nhltv_lib.game.is_home_game", return_value=True)
# game = create_game_object(igame)
# assert game.game_id == igame["gamePk"]
# assert game.is_home_game is True
# assert game.streams == igame["content"]["media"]["epg"][0]["items"]


# def test_create_game_object_away(mocker, games_data):
# igame = games_data["dates"][1]["games"][1]
# mocker.patch("nhltv_lib.game.is_home_game", return_value=False)
# game = create_game_object(igame)
# assert game.game_id == igame["gamePk"]
# assert game.is_home_game is False
# assert game.streams == igame["content"]["media"]["epg"][0]["items"]


# def test_is_home_game(mocker, mock_get_team_id):
# assert is_home_game(dict(teams=dict(home=dict(team=dict(id=18)))))
# assert not is_home_game(dict(teams=dict(home=dict(team=dict(id=19)))))
