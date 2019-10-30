import subprocess
import pytest
from nhltv_lib.process import (
    call_subprocess,
    call_subprocess_and_report_rc,
    verify_cmd_exists_in_path,
)
from nhltv_lib.exceptions import CommandMissing


def test_call_subprocess(mocked_subprocess):
    command = "testcommand"
    call_subprocess(command)
    mocked_subprocess.assert_called_with(
        command, stdout=subprocess.PIPE, shell=True
    )


def test_call_subprocess_and_report_rc(mocker):
    command = "testcommand"

    mocked_call_subprocess = mocker.patch("nhltv_lib.process.call_subprocess")
    mocked_call_subprocess.return_value.returncode = 0
    rc = call_subprocess_and_report_rc(command)

    mocked_call_subprocess.assert_called_with(command)
    assert rc


def test_call_subprocess_and_report_rc_neg(mocker):
    command = "testcommand"

    mocked_call_subprocess = mocker.patch("nhltv_lib.process.call_subprocess")
    mocked_call_subprocess.return_value.returncode = 1
    rc = call_subprocess_and_report_rc(command)

    mocked_call_subprocess.assert_called_with(command)
    assert not rc


def test_verify_cmd_exists_in_path(mocker):
    mocked_call_subprocess_rc = mocker.patch(
        "nhltv_lib.process.call_subprocess_and_report_rc", return_value=True
    )

    verify_cmd_exists_in_path("test")
    mocked_call_subprocess_rc.assert_called_with("which test")


def test_verify_cmd_exists_in_path_raises_CommandMissing(mocker):
    mocker.patch(
        "nhltv_lib.process.call_subprocess_and_report_rc", return_value=False
    )

    with pytest.raises(
        # pylint:disable=bad-continuation
        CommandMissing,
        match="test is missing, please install it",
    ):
        verify_cmd_exists_in_path("test")
