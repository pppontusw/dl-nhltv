from nhltv_lib.stream import get_quality, get_shorten_video


def test_get_quality(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert get_quality() == 3333


def test_get_shorten_video(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert not get_shorten_video()


def test_get_shorten_video_yes(mocker, ParsedArgs, parsed_args_list):
    parsed_args_list[8] = True
    mocker.patch(
        "nhltv_lib.arguments.parse_args",
        return_value=ParsedArgs(*parsed_args_list),
    )
    assert get_shorten_video()


def test_get_quality_none(mocker, ParsedArgs, parsed_args_list):
    parsed_args_list[2] = None
    mocker.patch(
        "nhltv_lib.arguments.parse_args",
        return_value=ParsedArgs(*parsed_args_list),
    )
    assert get_quality() == 5000
