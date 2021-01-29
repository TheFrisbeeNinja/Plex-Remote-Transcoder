"""The Configuration module contains all the functionality needed to store system specific data."""
import json
import logging
import os
from typing import List
from typing import Optional

from plex_remote_transcoder.node.server import Server

from .exceptions import FailedToDecodeJsonError
from .exceptions import NameRequiredError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


DEFAULT_CONFIG_JSON = {
    "pathScript": None,
    "serverScript": None,
    "servers": {"master": {}, "nodes": []},
    "loadBalanceStrategy": "minimumLoad",
    "plexAuthToken": None,
    "user": "plex",
    "environment": {}
}


# ----------------------------------------------------------------------------------------------------------------------
class Configuration(object):
    """Configuration object to provide programatic access to and from the configuration data."""

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, fileName: str):
        """Initalized the Configuration object with a file.

        Args:
            fileName (str): The file name to use for this configuration data.

        Exceptions:
            FailedToDecodeJsonException - Raised when the JSON decode from the provided file fails

        If the file is not found, then the default confguration data are used.
        """
        self._fileName = fileName
        if os.path.isfile(fileName):
            try:
                self._data = json.load(open(fileName, 'r'))
            except json.JSONDecodeError as e:
                raise FailedToDecodeJsonError(fileName, e)

        else:
            log.debug("Didn't find file {}, initializing to defaults".format(fileName))
            # No file to load, init to defaults
            self._data = DEFAULT_CONFIG_JSON

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def fileName(self) -> str:
        """The file where this configuration data is saved."""
        return self._fileName

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def user(self) -> str:
        """The user that Plex is configured to run as."""
        return self._data["user"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def loadBalanceStrategy(self) -> str:
        """The load balancing strategy to use when selecting servers."""
        return self._data["loadBalanceStrategy"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def plexAuthToken(self) -> str:
        """Returns the plexAuthToken."""
        return self._data["plexAuthToken"]

    @plexAuthToken.setter
    def plexAuthToken(self, newToken: str) -> None:
        self._data["plexAuthToken"] = newToken

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def servers(self) -> List[Server]:
        """All the servers in this configuration."""
        output = []
        for node in self._data["servers"]["nodes"]:
            server = Server("tmp")
            server.fromJson(node)
            output.append(server)
        return output

    # ------------------------------------------------------------------------------------------------------------------
    def getEnvironmentVariable(self, name: str) -> str:
        """Returns the value of the specified variable.

        Args:
            name (str): The variable name.
        """
        if name in self._data["environment"]:
            return self._data["environment"][name]
        else:
            return None

    # ------------------------------------------------------------------------------------------------------------------
    def setEnvironmentVariable(self, name: str, value: str) -> None:
        """Sets the value of the specified variable.

        Args:
            name (str): The variable name.
            value (str): The new value to set.
        """
        self._data["environment"][name] = value

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def master(self) -> Server:
        """The master server for this configuration."""
        server = Server("tmp")
        server.fromJson(self._data["servers"]["master"])
        return server

    @master.setter
    def master(self, newMaster):
        self._data["servers"]["master"] = newMaster.__repr__()

    # ------------------------------------------------------------------------------------------------------------------
    def getServersInGroup(self, group: Optional[str] = None) -> List[Server]:
        """Returns the servers in the the group.

        Args:
            group (str): The group to search for.
        """
        if group is None:
            return self.servers
        else:
            return [server for server in self._data["servers"] if server.group == group]

    # ------------------------------------------------------------------------------------------------------------------
    def getServerByName(self, name: str) -> Server:
        """Returns the server information identified by name.

        Args:
            name (str): The name of the server to look for.
        """
        for server in self._data["servers"]:
            if server.name == name:
                return server
        return None

    # ------------------------------------------------------------------------------------------------------------------
    def addServer(self, newServer: Server) -> bool:
        """Adds a server to the configuration.

        Args:
            newServer (Server): A server object to add to the configuration.

        If this server is already represented in the configuration this function will return False.
        """
        if not isinstance(newServer, Server):
            return False

        for server in self.servers:
            if server == newServer:
                log.debug("Rejecting new server {} due to match with {}".format(newServer, server))
                return False

        self._data["servers"]["nodes"].append(newServer.__repr__())
        log.debug("New server {} added to configuration".format(newServer))
        return True

    # ------------------------------------------------------------------------------------------------------------------
    def removeServer(self, name: str) -> bool:
        """Removes a server from the configuration.

        Args:
            name (str): The server name to remove.
        """
        if name is None:
            log.error("Need a NAME to remove server!")
            raise NameRequiredError()

        for server in self._data["servers"]["nodes"]:
            if name == server["name"]:
                self._data["servers"]["nodes"].remove(server)
                return True
        else:
            log.debug("Failed to find a server with Name = {}".format(name))
            return False

    # ------------------------------------------------------------------------------------------------------------------
    def writeToDisk(self):
        """Writes the configuration data to disk."""
        with open(self._fileName, "w+") as fileHandle:
            json.dump(self._data, fileHandle, sort_keys=True, indent=4)
