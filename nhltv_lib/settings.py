import os
from nhltv_lib.arguments import get_arguments


def get_download_folder():
    """
    Which folder should we download to?
    """
    args = get_arguments()

    return args.download_folder or os.getcwd()


def get_retentiondays():
    """
    How many days should we retain videos?
    """
    args = get_arguments()

    if args.retentiondays:
        retentiondays = int(args.retentiondays)
    else:
        retentiondays = None

    return retentiondays
