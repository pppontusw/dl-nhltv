import os
from nhltv_lib.settings import get_download_folder, get_retentiondays


def test_get_download_folder():

    assert get_download_folder() == os.getcwd() + "/test"


def test_get_retentiondays():
    assert get_retentiondays() == 4


def test_get_retentiondays_none(
    mocker, mocked_parse_args, parsed_args, parsed_args_list
):
    parsed_args_list[6] = None
    mocked_parse_args.return_value = parsed_args(*parsed_args_list)
    assert get_retentiondays() is None
