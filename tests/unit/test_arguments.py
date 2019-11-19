import os
import pytest
from nhltv_lib.arguments import parse_args


def test_parse_args(arguments_list):
    argies = parse_args(arguments_list)
    assert argies.username == "username"
    assert argies.password == "password"
    assert argies.quality == "3333"
    assert argies.checkinterval == "4"
    assert argies.download_folder == os.getcwd() + "/test"
    assert argies.retentiondays == "5"
    assert argies.preferred_stream == ["FS-TN"]


def test_parse_args_multipref_stream(arguments_list):
    arguments_list += ["--prefer-stream", "CBS"]
    argies = parse_args(arguments_list)
    assert argies.preferred_stream == ["FS-TN", "CBS"]


def test_parse_args_no_stream(arguments_list):
    arguments_list = arguments_list[:14]
    argies = parse_args(arguments_list)
    assert argies.preferred_stream is None


def test_parse_args_requires_required_props(arguments_list):
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "username" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "password" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "team" not in i])
