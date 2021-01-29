"""Exceptions for the plex package."""


# ----------------------------------------------------------------------------------------------------------------------
class PlexError(Exception):
    """Base exception class for Plex exceptions."""


# ----------------------------------------------------------------------------------------------------------------------
class XmlTagMismatchError(PlexError):
    """Exception raised when XML tags do not match."""
    def __init__(self, desiredTag: str, foundTag: str):
        """Initializes the exception.

        Args:
            desiredTag (str): The tag attempting to match.
            foundTag (str): The tag that was found.
        """
        super().__init__("Failed to match XML tags - Expected {} - Found {}".format(desiredTag, foundTag))
        self.desiredTag = desiredTag
        self.foundTag = foundTag


# ----------------------------------------------------------------------------------------------------------------------
class LocalTranscoderFoundError(PlexError):
    """Exception raised when the local transcoder has already been installed."""
    def __init__(self, path):
        """Initializes the exception.

        Args:
            path (str): The path of the found transcoder
        """
        super().__init__("Found existing local transcoder at {}".format(path))
        self.path = path


# ----------------------------------------------------------------------------------------------------------------------
class RemoteTranscoderFoundError(PlexError):
    """Exception raised when the remote transcoder has already been installed."""
    def __init__(self, path):
        """Initializes the exception.

        Args:
            path (str): The path of the found transcoder
        """
        super().__init__("Found existing remote transcoder at {}".format(path))
        self.path = path


# ----------------------------------------------------------------------------------------------------------------------
class RemoteTranscoderExeNotFoundError(PlexError):
    """Exception raised when the transcoder program cannot be found."""
    def __init__(self):
        """Initializes the exception."""
        super().__init__("Failed to find the remote transcoder executable!")
