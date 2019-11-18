import os
import logging


def setup_logging():
    logger = logging.getLogger("nhltv")

    logger.setLevel("DEBUG")

    console_handler = logging.StreamHandler()

    os.makedirs("logs", exist_ok=True)
    file_handler = logging.FileHandler("logs/nhltv.log")

    c_format = logging.Formatter(
        "%(asctime)s - %(funcName)s - %(levelname)s - %(message)s"
    )
    f_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(c_format)
    file_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logger.debug("Logger initialized")
