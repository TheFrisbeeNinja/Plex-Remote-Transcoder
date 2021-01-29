"""Exceptions for the Configuration package."""
from json import JSONDecodeError


# ----------------------------------------------------------------------------------------------------------------------
class ConfigurationError(Exception):
    """Base exception class for Configuration exceptions."""


# ----------------------------------------------------------------------------------------------------------------------
class PathNotFound(ConfigurationError):
    """Raised when a path cannot be found on disk."""

    def __init__(self, path: str) -> None:
        """Initializes PathNotFound.

        Args:
            path (str): The path that cannot be located.
        """
        super().__init__("Failed to find path {}".format(path))
        self.path = path


# ----------------------------------------------------------------------------------------------------------------------
class PathFoundError(ConfigurationError):
    """Raised when a path aready exists."""

    def __init__(self, path: str) -> None:
        """Initializes the exception.

        Args:
            path (str): The path that exists.
        """
        super().__init__("Path {} already exists".format(path))
        self.path = path


# ----------------------------------------------------------------------------------------------------------------------
class FailedToDecodeJsonError(ConfigurationError):
    """Raised when JSON files fail decoding, typically on load."""

    def __init__(self, fileName: str, exception: JSONDecodeError) -> None:
        """Initializes FailedToDecodeJsonErrorError.

        Args:
            fileName (str): The name of the file that failed decode.
            exception (JSONDecodeError): The exception thrown by the json package
        """
        message_lines = [
            "Failed to decode JSON from file {}.".format(fileName),
            "{}".format(exception)
        ]
        super().__init__("".join(message_lines))
        self.fileName = fileName


# ----------------------------------------------------------------------------------------------------------------------
class NameRequiredError(ConfigurationError):
    """Raised when a name has not been provided."""

    def __init__(self):
        """Initializes the error."""
        super().__init__("Operation requires a name")


# ----------------------------------------------------------------------------------------------------------------------
class EnvVarNotFoundError(ConfigurationError):
    """Raised when an environment variable is not found."""

    def __init__(self, name: str):
        """Initializes the error.

        Args:
            name (str): The name of the variable.
        """
        super().__init__("No value found for variable {}".format(name))
        self.name = name
