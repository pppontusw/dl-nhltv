from datetime import datetime, timedelta
from nhltv_lib.waitlist import (
    get_archive_wait_list,
    add_game_to_archive_wait_list,
    filter_out_old_entries,
    get_blackout_wait_list,
    add_game_to_blackout_wait_list,
)


def test_get_archive_wait_list(mocker):
    mocker.patch("nhltv_lib.waitlist.read_json_dict")
    mocker.patch(
        "nhltv_lib.waitlist.filter_out_old_entries",
        return_value={"3000": "5000"},
    )
    assert get_archive_wait_list() == {"3000": "5000"}


def test_add_game_to_blackout_wait_list(mocker):
    da = datetime.now()
    mockfunc = mocker.patch("nhltv_lib.waitlist.add_to_json_dict")
    mocktime = mocker.patch("nhltv_lib.waitlist.datetime")
    mocktime.now.return_value = da
    add_game_to_blackout_wait_list(123)
    mockfunc.assert_called_once_with(
        "blackout_waitlist", {"123": (da + timedelta(hours=4)).isoformat()}
    )


def test_get_blackout_wait_list(mocker):
    mocker.patch("nhltv_lib.waitlist.read_json_dict")
    mocker.patch(
        "nhltv_lib.waitlist.filter_out_old_entries",
        return_value={"3000": "5000"},
    )
    assert get_blackout_wait_list() == {"3000": "5000"}


def test_add_game_to_archive_wait_list(mocker):
    da = datetime.now()
    mockfunc = mocker.patch("nhltv_lib.waitlist.add_to_json_dict")
    mocktime = mocker.patch("nhltv_lib.waitlist.datetime")
    mocktime.now.return_value = da
    add_game_to_archive_wait_list(123)
    mockfunc.assert_called_once_with(
        "archive_waitlist", {"123": (da + timedelta(minutes=15)).isoformat()}
    )


def test_filter_out_old_entries():
    da = datetime.now()
    times = {
        1: (da - timedelta(minutes=10)).isoformat(),
        2: (da).isoformat(),
        3: (da + timedelta(minutes=10)).isoformat(),
    }

    assert dict(filter_out_old_entries(times)) == {
        3: (da + timedelta(minutes=10)).isoformat()
    }
