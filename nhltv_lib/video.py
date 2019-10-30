from nhltv_lib.arguments import get_arguments


def get_obfuscate():
    """
    Should the video be obfuscated?
    """
    args = get_arguments()

    return args.obfuscate
