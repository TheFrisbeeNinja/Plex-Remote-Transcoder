"""Module for dealing with Plex API."""
import base64
import hashlib

from plex_remote_transcoder import VERSION as PRT_VERSION
import requests
from requests.exceptions import HTTPError

CLIENT_STRING = "Plex-Remote-Transcoder-v" + PRT_VERSION


# ----------------------------------------------------------------------------------------------------------------------
def fetchAuthToken(username: str, password: str) -> str:
    """Fetches the user's token from the Plex servers.

    Args:
        username (str): The username of the Plex account.
        password (str): The password of the Plex account.
    """
    clientId = hashlib.sha512(CLIENT_STRING.encode()).hexdigest()
    userId = base64.b64encode("{}:{}".format(username, password).encode())

    headers = {"Authorization": "Basic {}".format(userId.decode('ascii')),
               "X-Plex-Client-Identifier": clientId,
               "X-Plex-Product": "Plex-Remote-Transcoder",
               "X-Plex-Version": PRT_VERSION}

    try:
        response = requests.post("https://plex.tv/users/sign_in.json", headers=headers)
        response.raise_for_status()
    except HTTPError as err:
        raise err

    data = response.json()

    return data["user"]["authToken"]


# ----------------------------------------------------------------------------------------------------------------------
class Server(object):
    """Class for running commands against a Plex API."""
    def __init__(self, serverAddress: str, serverPort: int, authToken: str):
        """Initialize the server object.

        Args:
            serverAddress (str): The address of the Plex server
            serverPort (int): The port of the Plex server
            authToken (str): The user autorization token
        """
        self._serverAddress = serverAddress
        self._serverPort = serverPort
        self._authToken = authToken

    # ------------------------------------------------------------------------------------------------------------------
    def fetchSessionData(self) -> str:
        """Returns the session data from the plex server."""
        headers = {"X-Plex-Token": self._authToken}

        try:
            response = requests.get("http://{}:{}/status/sessions".format(self._serverAddress, self._serverPort), headers=headers)
            response.raise_for_status()
        except HTTPError as err:
            raise err

        return response.content

    # ------------------------------------------------------------------------------------------------------------------
    def get(self, resource: str) -> str:
        """Returns the result of a GET request from the Plex resource.

        Args:
            resource (str): The resource to run the GET request on
        """
        headers = {"X-Plex-Token": self._authToken}
        try:
            response = requests.get("http://{}:{}{}".format(self._serverAddress, self._serverPort, resource), headers=headers)
            response.raise_for_status()
        except HTTPError as err:
            raise err

        return response.content
