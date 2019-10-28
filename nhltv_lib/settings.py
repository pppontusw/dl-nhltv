import os
from collections import namedtuple

AppSettings = namedtuple(
    "AppSettings",
    [
        "quality",
        "download_folder",
        "checkinterval",
        "retentiondays",
        "days_back_to_search",
        "obfuscate",
        "shorten_video",
    ],
)


def get_settings_from_arguments(arguments):
    """
    Create a settings object from parsed arguments
    """

    quality = int(arguments.quality) or 5000
    download_folder = arguments.download_folder or os.getcwd()
    checkinterval = int(arguments.checkinterval) or 60
    retentiondays = int(arguments.retentiondays) or 14
    days_back_to_search = int(arguments.days_back_to_search) or 3

    if arguments.obfuscate is None:
        obfuscate = False
    else:
        obfuscate = arguments.obfuscate

    shorten_video = arguments.shorten_video or False

    settings = AppSettings(
        quality,
        download_folder,
        checkinterval,
        retentiondays,
        days_back_to_search,
        obfuscate,
        shorten_video,
    )
    return settings
