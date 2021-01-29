"""Exceptions for the autoeditor package."""


# ----------------------------------------------------------------------------------------------------------------------
class AutoEditorError(Exception):
    """Base exception class for AutoEditor exceptions."""


# ----------------------------------------------------------------------------------------------------------------------
class MarkerNotFoundError(AutoEditorError):
    """Raised when the specified marker is not found."""

    def __init__(self, fileName: str, marker: str) -> None:
        """Initializes MarkerNotFoundError.

        Args:
            fileName (str): The name of the file that failed.
            marker (str): The marker ID that was not found
        """
        super().__init__("Failed to find markerID={} in {}".format(marker, fileName))
        self.fileName = fileName
        self.markerId = marker


# ----------------------------------------------------------------------------------------------------------------------
class MarkerAlreadyExistsError(AutoEditorError):
    """Raised when the specified marker already exists in the file."""

    def __init__(self, fileName: str, marker: str) -> None:
        """Initializes MarkerAlreadyExistsError.

        Args:
            fileName (str): The name of the file that failed.
            marker (str): The marker ID that was found.
        """
        super().__init__("markerID={} already exists in {}".format(marker, fileName))
        self.fileName = fileName
        self.markerId = marker
