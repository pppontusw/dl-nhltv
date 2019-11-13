from nhltv_lib.downloaded_games import get_downloaded_games


def test_get_downloaded_games(mocker):
    mocked_rjsf = mocker.patch("nhltv_lib.downloaded_games.read_json_list")
    assert get_downloaded_games() == mocked_rjsf("downloaded_games")
