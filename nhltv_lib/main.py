import logging
from nhltv_lib.auth import NHLTVUser
from nhltv_lib.logger import setup_logging
from nhltv_lib.arguments import get_arguments
from nhltv_lib.process import verify_cmd_exists_in_path

logger = logging.getLogger("nhltv")


def verify_dependencies():
    dependent_commands = ["ffmpeg", "aria2c"]

    for i in dependent_commands:
        verify_cmd_exists_in_path(i)


def main():
    arguments = get_arguments()

    setup_logging()
    verify_dependencies()

    nhltv_user = NHLTVUser(arguments.username, arguments.password)
    logger.debug("Set nhltv_user to %s", nhltv_user)


if __name__ == "__main__":
    main()
