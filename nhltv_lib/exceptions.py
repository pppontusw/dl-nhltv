class CommandMissing(Exception):
    """
    Some required command is missing
    """


class AuthenticationFailed(Exception):
    """
    Failed to log in to NHLTV
    """


class RequestFailed(Exception):
    """
    An external API call failed
    """


class BlackoutRestriction(Exception):
    """
    This game is blacked out
    """


class ExternalProgramError(Exception):
    """
    An external program has quit with an error
    """


class DownloadError(Exception):
    """
    Downloading file failed
    """


class DecodeError(Exception):
    """
    Decoding video files failed
    """
