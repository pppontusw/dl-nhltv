from typing import Tuple, Iterator, List, Callable
import subprocess
from nhltv_lib.exceptions import CommandMissing, ExternalProgramError
from nhltv_lib.common import tprint


def call_subprocess(command: str) -> subprocess.Popen:
    """
    Calls a subprocess and returns it
    """
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=False,
    )


def call_subprocess_and_get_stdout_iterator(
    command: str, timeout: int = 1800
) -> Tuple[subprocess.Popen, Iterator[bytes]]:
    """
    Starts a subprocess with command and returns the process object
    as well as an iterator over stdout
    """
    proc = call_subprocess(command)
    try:
        stdout, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        proc.kill()
        stdout, _ = proc.communicate()
        raise ExternalProgramError(
            "Subprocess timed out and was killed."
        ) from e
    return proc, iter(stdout.splitlines())


def call_subprocess_and_report_rc(command: str, timeout: int = 1800) -> bool:
    """
    Calls a subprocess and returns True if the return code is 0 after it finishes
    """
    process = call_subprocess(command)
    try:
        _, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        process.kill()
        _, stderr = process.communicate()
        raise ExternalProgramError(
            "Subprocess timed out and was killed."
        ) from e
    if process.returncode != 0:
        raise ExternalProgramError(stderr)
    return True


def call_subprocess_and_raise_on_error(
    command: str, error: Callable = ExternalProgramError, timeout: int = 1800
) -> List[bytes]:
    """
    Calls subprocess with command and raises *error* if returncode is not 0
    Returns stdout as a list of bytes otherwise
    """
    process = call_subprocess(command)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as e:
        process.kill()
        stdout, stderr = process.communicate()
        raise error("Subprocess timed out and was killed.") from e
    if process.returncode != 0:
        raise error(stderr)
    return stdout.splitlines()


def verify_cmd_exists_in_path(cmd: str) -> None:
    """
    Verifies that *cmd* exists by running `which {cmd}` and ensuring rc is 0
    """
    tprint(f"Checking for {cmd}..", debug_only=True)
    if not call_subprocess_and_report_rc(f"which {cmd}"):
        raise CommandMissing(f"{cmd} is missing, please install it")
    tprint(f"{cmd} exists", debug_only=True)
