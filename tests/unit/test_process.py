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
