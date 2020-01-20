from typing import Tuple, Iterable, List, Callable
import subprocess
from nhltv_lib.exceptions import CommandMissing, ExternalProgramError
from nhltv_lib.common import tprint


def call_subprocess(command: str) -> subprocess.Popen:
    """
    Calls a subprocess and returns it
    """
    return subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )


def call_subprocess_and_get_stdout_iterator(
    command: str
) -> Tuple[subprocess.Popen, Iterable[bytes]]:
    """
    Starts a subprocess w/ command and returns the process object
    as well as an iterator over stdout
    """
    proc = call_subprocess(command)
    pi = iter(proc.stdout.readline, b"")
    return proc, pi


def call_subprocess_and_report_rc(command: str) -> bool:
    """
    Calls a subprocess and returns the returncode after it finishes
    """
    process = call_subprocess(command)
    process.wait()
    return process.returncode == 0


def call_subprocess_and_raise_on_error(
    command: str, error: Callable = ExternalProgramError
) -> List[bytes]:
    """
    Calls subprocess w/ command and raises *error* if returncode is not 0
    Returns stdout.readlines() otherwise
    """
    p = call_subprocess(command)
    p.wait()
    if p.returncode != 0:
        raise error(p.stdout.readlines())
    else:
        return p.stdout.readlines()


def verify_cmd_exists_in_path(cmd: str) -> None:
    """
    Verifies that *cmd* exists by running `which {cmd}` and ensuring rc is 0
    """
    tprint(f"Checking for {cmd}..", debug_only=True)
    if not call_subprocess_and_report_rc(f"which {cmd}"):
        raise CommandMissing(f"{cmd} is missing, please install it")
    tprint(f"{cmd} exists", debug_only=True)
