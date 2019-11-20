import subprocess
import pytest
from nhltv_lib.process import (
    call_subprocess,
    call_subprocess_and_report_rc,
    verify_cmd_exists_in_path,
    call_subprocess_and_raise_on_error,
)
from nhltv_lib.exceptions import (
    CommandMissing,
    ExternalProgramError,
    DecodeError,
)


@pytest.fixture(scope="function", autouse=True)
def mocked_call_subprocess(mocker):
    return mocker.patch("nhltv_lib.process.call_subprocess")


def test_call_subprocess(mocked_subprocess):
    command = "testcommand"
    call_subprocess(command)
    mocked_subprocess.assert_called_with(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )


def test_call_subprocess_and_report_rc(mocker, mocked_call_subprocess):
    command = "testcommand"

    mocked_call_subprocess.return_value.returncode = 0
    rc = call_subprocess_and_report_rc(command)

    mocked_call_subprocess.assert_called_with(command)
    assert rc


def test_call_subprocess_and_report_rc_neg(mocker, mocked_call_subprocess):
    command = "testcommand"

    mocked_call_subprocess.return_value.returncode = 1
    rc = call_subprocess_and_report_rc(command)

    mocked_call_subprocess.assert_called_with(command)
    assert not rc


def test_call_subp_and_raise(mocker, mocked_call_subprocess):
    mocked_call_subprocess().returncode = 0
    call_subprocess_and_raise_on_error("foo")


def test_call_subp_and_raise_default_error(mocker, mocked_call_subprocess):
    mocked_call_subprocess().returncode = 1
    with pytest.raises(ExternalProgramError):
        call_subprocess_and_raise_on_error("boo")


def test_call_subp_and_raise_custom_error(mocker, mocked_call_subprocess):
    mocked_call_subprocess().returncode = 1
    with pytest.raises(DecodeError):
        call_subprocess_and_raise_on_error("boo", DecodeError)


def test_verify_cmd_exists_in_path(mocker):
    mocked_call_subprocess_rc = mocker.patch(
        "nhltv_lib.process.call_subprocess_and_report_rc", return_value=True
    )

    verify_cmd_exists_in_path("test")
    mocked_call_subprocess_rc.assert_called_with("which test")


def test_verify_cmd_exists_in_path_raises_commandmissing(mocker):
    mocker.patch(
        "nhltv_lib.process.call_subprocess_and_report_rc", return_value=False
    )

    with pytest.raises(
        # pylint:disable=bad-continuation
        CommandMissing,
        match="test is missing, please install it",
    ):
        verify_cmd_exists_in_path("test")
