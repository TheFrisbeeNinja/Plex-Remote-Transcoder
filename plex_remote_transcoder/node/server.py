"""The Server module contains all the functionality needed to interact with a node."""
import json
import logging
import subprocess
from shlex import quote as escapeQuotes
from typing import Dict
from typing import List

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# ----------------------------------------------------------------------------------------------------------------------
class Server(object):
    """Provides storage and modification of server properties."""

    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, name: str):
        """Initializes the Server object with a name.

        Args:
            name (str): The name of the server.
        """
        self._data = {"name": name,
                      "ipAddress": None,
                      "user": None,
                      "port": None,
                      "group": None}

    # ------------------------------------------------------------------------------------------------------------------
    def ping(self) -> bool:
        """Pings the server with a simple SSH check."""
        command = ["ssh", "-p", str(self.port), "-T", "{}@{}".format(self.user, self.ipAddress), "true"]
        log.debug("Executing command -->> {}".format(" ".join(command)))
        response = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode == 0

    # ------------------------------------------------------------------------------------------------------------------
    def getLoad(self) -> (int, List[int]):
        """Returns the load stats for this server."""
        command = ["ssh", "-p", str(self.port), "{}@{}".format(self.user, self.ipAddress), "prt3", "get-load"]
        log.debug("Executing command --> {}".format(" ".join(command)))
        response = subprocess.run(command, stdout=subprocess.PIPE)
        load = [int(i) for i in response.stdout.split()]
        return (response.returncode, load)

    # ------------------------------------------------------------------------------------------------------------------
    def transcode(self, environment: Dict[str, str], workingDir: str, arguments: List[str]) -> int:

        # Step 1 - Build 'export key=value' string
        envExports = ";".join(["export {}={}".format(key, escapeQuotes(value)) for key, value in environment.items()])

        # Step 2 - Build the CHDIR command
        changeDir = "cd {}".format(workingDir)

        # Step 3 - Build the transcode command
        transcode = "/usr/lib/plexmediaserver/prt_local_transcoder " + " ".join(escapeQuotes(arg) for arg in arguments)

        # Step 4 - Assemble command to execute
        transcodeCommand = envExports + ";" + changeDir + ";" + transcode

        command = ["ssh", "-p", str(self.port), "{}@{}".format(self.user, self.ipAddress), transcodeCommand]
        log.debug("Executing command --> {}".format(" ".join(command)))

        response = subprocess.run(command, stdout=subprocess.PIPE)

        return response.returncode

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def name(self) -> str:
        """The name of the server."""
        return self._data["name"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def ipAddress(self) -> str:
        """The IP Address of the server."""
        return self._data["ipAddress"]

    @ipAddress.setter
    def ipAddress(self, newIpAddress: str) -> None:
        self._data["ipAddress"] = newIpAddress

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def port(self) -> int:
        """The port number to use to SSH to the server."""
        return self._data["port"]

    @port.setter
    def port(self, newPort: int) -> None:
        self._data["port"] = newPort

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def group(self) -> str:
        """The group this server belongs in."""
        return self._data["group"]

    @group.setter
    def group(self, newGroup: str) -> None:
        self._data["group"] = newGroup

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def user(self) -> str:
        """The user to use when connecting to the server."""
        return self._data["user"]

    @user.setter
    def user(self, newUser: str) -> None:
        self._data["user"] = newUser

    # ------------------------------------------------------------------------------------------------------------------
    def toJson(self) -> str:
        """Returns the JSON representation of this object."""
        return json.dumps(self._data)

    # ------------------------------------------------------------------------------------------------------------------
    def fromJson(self, data):
        """Overwrites the internal data with new data."""
        self._data = data

    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self) -> str:
        """String representation of the object.

        In this case we're doing some pretty printing to make displays easier for humans.
        """
        return "{}/{} ({}@{}:{})".format(self.group, self.name, self.user, self.ipAddress, self.port)

    # ------------------------------------------------------------------------------------------------------------------
    def __repr__(self) -> dict:
        """Python representation of the object.

        Easy to use the dictionary object here.
        """
        return self._data

    # ------------------------------------------------------------------------------------------------------------------
    def __eq__(self, other) -> bool:
        """Compares server objects to each other.

        To avoid nasty errors down the road, if either the IP address or the name matches, we'll return True.
        """
        if self.ipAddress == other.ipAddress or self.name == other.name:
            return True
        else:
            return False

    # ------------------------------------------------------------------------------------------------------------------
    def __ne__(self, other) -> bool:
        """Compares server objects to each other."""
        return not self.__ne__(other)
