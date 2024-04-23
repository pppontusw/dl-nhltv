import os
import logging


def setup_logging():
    logger = logging.getLogger("nhltv")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/nhltv.log")
    file_handler.setLevel(logging.ERROR)

    c_format = logging.Formatter("%(funcName)s - %(levelname)s - %(message)s")
    f_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(c_format)
    file_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized")
