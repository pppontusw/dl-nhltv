import os
import pytest
from nhltv_lib.arguments import parse_args


def test_parse_args(arguments_list):
    argies = parse_args(arguments_list)
    assert argies.username == "username"
    assert argies.password == "password"
    assert argies.checkinterval == "4"
    assert argies.download_folder == os.getcwd() + "/test"
    assert argies.retentiondays == "5"


def test_parse_args_requires_required_props(arguments_list):
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "username" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "password" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "team" not in i])
