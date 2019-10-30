from nhltv_lib.video import get_obfuscate


def test_get_obfuscate(mocker, parsed_arguments):
    mocker.patch(
        "nhltv_lib.arguments.parse_args", return_value=parsed_arguments
    )
    assert get_obfuscate()


def test_get_obfuscate_from_args_false(mocker, ParsedArgs, parsed_args_list):
    parsed_args_list[7] = False
    mocker.patch(
        "nhltv_lib.arguments.parse_args",
        return_value=ParsedArgs(*parsed_args_list),
    )
    assert not get_obfuscate()
