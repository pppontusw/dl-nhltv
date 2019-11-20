from typing import Optional
import os
from nhltv_lib.arguments import get_arguments


def get_download_folder() -> str:
    """
    Which folder should we download to?
    """
    args = get_arguments()

    return args.download_folder or os.getcwd()


def get_retentiondays() -> Optional[int]:
    """
    How many days should we retain videos?
    """
    args = get_arguments()

    if args.retentiondays:
        retentiondays: Optional[int] = int(args.retentiondays)
    else:
        retentiondays = None

    return retentiondays
