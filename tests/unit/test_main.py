import sys
import pytest
from nhltv_lib.main import main, verify_dependencies
from nhltv_lib.arguments import parse_args


@pytest.mark.skip
def test_main_calls_parse_args_with_arguments_list(mocker, arguments_list):
    mock_parse_args = mocker.patch("nhltv_lib.arguments.parse_args")
    mocker.patch("nhltv_lib.main.get_games_to_download")
    args_list = ["something"]
    args_list.append(arguments_list)

    mocker.patch("logging.getLogger")
    mocker.patch.object(sys, "argv", args_list)

    main()
    mock_parse_args.assert_called_with(args_list[1:])


@pytest.mark.skip
def test_main_calls_setup_logging(mocker):
    mocker.patch("nhltv_lib.arguments.parse_args")
    mocker.patch("nhltv_lib.main.get_games_to_download")
    mock_setup_logging = mocker.patch("nhltv_lib.main.setup_logging")
    main()
    mock_setup_logging.assert_called_once()


def test_verify_deps(mocker):
    mock_verify_deps = mocker.patch("nhltv_lib.main.verify_cmd_exists_in_path")
    verify_dependencies()
    mock_verify_deps.assert_called()


def test_parse_args_requires_username_and_password(arguments_list):
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "username" not in i])
    with pytest.raises(SystemExit):
        parse_args([i for i in arguments_list if "password" not in i])


def test_parse_args_parses_username_and_password(arguments_list):
    assert parse_args(arguments_list).username == "username"
    assert parse_args(arguments_list).password == "password"
