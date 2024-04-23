import sys
import pytest
from nhltv_lib.main import main, parse_args


def test_main_calls_parse_args_with_arguments_list(mocker, arguments_list):
    mock_parse_args = mocker.patch("nhltv_lib.main.parse_args")
    args_list = ["something"]
    args_list.append(arguments_list)

    mocker.patch("logging.getLogger")
    mocker.patch.object(sys, "argv", args_list)

    main()
    mock_parse_args.assert_called_with(args_list[1:])


def test_main_calls_setup_logging(mocker):
    mocker.patch("nhltv_lib.main.parse_args")
    mock_setup_logging = mocker.patch("nhltv_lib.main.setup_logging")
    main()
    mock_setup_logging.assert_called_once()


def test_parse_args_requires_username_and_password(arguments_list):
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "username" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "password" not in i])


def test_parse_args_parses_username_and_password(arguments_list):
    assert parse_args(arguments_list).username == "username"
    assert parse_args(arguments_list).password == "password"
