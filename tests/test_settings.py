import os
from nhltv_lib.settings import get_settings_from_arguments


def test_get_settings_from_arguments_normal(parsed_arguments):
    settings = get_settings_from_arguments(parsed_arguments)
    assert settings.quality == 3333
    assert settings.download_folder == os.getcwd() + "/test"
    assert settings.checkinterval == 10
    assert settings.retentiondays == 4
    assert settings.days_back_to_search == 2
    assert settings.obfuscate
    assert not settings.shorten_video


def test_get_settings_from_arguments_no_obfuscate(
    ParsedArgs, parsed_args_list
):
    parsed_args_list[7] = False
    settings = get_settings_from_arguments(ParsedArgs(*parsed_args_list))
    assert settings.quality == 3333
    assert settings.download_folder == os.getcwd() + "/test"
    assert settings.checkinterval == 10
    assert settings.retentiondays == 4
    assert settings.days_back_to_search == 2
    assert not settings.obfuscate
    assert not settings.shorten_video
