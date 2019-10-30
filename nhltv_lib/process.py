import subprocess
import logging
from nhltv_lib.exceptions import CommandMissing

logger = logging.getLogger("nhltv")


def call_subprocess(command):
    return subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)


def call_subprocess_and_report_rc(command):
    process = call_subprocess(command)
    process.wait()
    return process.returncode == 0


def verify_cmd_exists_in_path(cmd):
    logger.debug("Checking for %s..", cmd)
    if not call_subprocess_and_report_rc(f"which {cmd}"):
        raise CommandMissing(f"{cmd} is missing, please install it")
    logger.debug("%s exists", cmd)
