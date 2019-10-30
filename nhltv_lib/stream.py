from nhltv_lib.arguments import get_arguments


def get_quality():
    """
    Get quality from parsed args
    """
    args = get_arguments()

    if not args.quality:
        quality = 5000
    else:
        quality = int(args.quality)

    return quality


def get_shorten_video():
    """
    Are we shortening the video?
    """
    args = get_arguments()

    return args.shorten_video
