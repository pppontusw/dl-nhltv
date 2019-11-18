import os
from nhltv_lib.settings import get_download_folder, get_retentiondays


def test_get_download_folder(mocker, parsed_arguments):

    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )

    assert get_download_folder() == os.getcwd() + "/test"


def test_get_retentiondays(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert get_retentiondays() == 4


def test_get_retentiondays_none(mocker, ParsedArgs, parsed_args_list):
    parsed_args_list[6] = None
    mocker.patch(
        "nhltv_lib.arguments.parse_args",
        return_value=ParsedArgs(*parsed_args_list),
    )
    assert get_retentiondays() is None
