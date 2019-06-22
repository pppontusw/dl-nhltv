
class BlackoutRestriction(Exception):
    """Tried to download Blackout Restricted game! """


class NoGameFound(Exception):
    """When checking for the next game we could not find one """


class GameStartedButNotAvailableYet(Exception):
    """When checking for the next game we found one but is not available for download yet """


class DownloadError(Exception):
    """Failed to download video using Aria2"""


class ExternalProgramError(Exception):
    """Execution of an external program failed"""


class DecodeError(Exception):
    """Failed to decode files"""


class CredentialsError(Exception):
    """No credentials or login failed"""
