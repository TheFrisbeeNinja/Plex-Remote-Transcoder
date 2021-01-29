"""Module for writing information into the SSH configuration files needed to interact with the PRT nodes."""
import logging
import os
import pathlib

from plex_remote_transcoder.autoeditor.file import File as AutoEditorFile
from plex_remote_transcoder.node.server import Server

from .exceptions import PathNotFound

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# ----------------------------------------------------------------------------------------------------------------------
def installGlobalConfigInclude(sshConfigFile: str, pathToConfigs: str) -> None:
    """Adds the include to the global SSH config file to pull in all the PRT server info.

    Args:
        sshConfigFile (str): The SSH config file to update.
        pathToConfigs (str): The path where all the PRT server configurations are stored.
    """
    configurationLines = ["Include {}".format(os.path.join(pathToConfigs, "*.prt"))]

    if not os.path.isdir(pathToConfigs):
        log.debug("Path {} not found, attempting to create...".format(pathToConfigs))
        os.makedirs(pathToConfigs)

    configFile = AutoEditorFile(sshConfigFile, commentCharacters="#", markerLabel="PRT SSH Server Config")

    if os.path.isfile(sshConfigFile):
        log.debug("{} already exists, overwritting autoeditor section...".format(sshConfigFile))
        configFile.addOrReplaceLinesInMarker("GLOBAL-SSH", configurationLines)
    else:
        log.debug("{} not found, create new file...".format(sshConfigFile))
        pathlib.Path(sshConfigFile).touch()
        os.chmod(sshConfigFile, 0o600)
        configFile.addNewMarker("GLOBAL-SSH", configurationLines)


# ----------------------------------------------------------------------------------------------------------------------
def writeConfigFileForServer(path: str, server: Server) -> None:
    """Writes the SSH config file for a server to the path provided.

    Args:
        path (str): The path where the SSH config file is to be stored
        server (Server): The server object to write a config file for
    """
    if not os.path.isdir(path):
        raise PathNotFound(path)

    configurationLines = ["Host {}".format(server.name),
                          "Hostname {}".format(server.ipAddress),
                          "User {}".format(server.user),
                          "Port {}".format(server.port)]

    fileName = os.path.join(path, server.name + ".ptr")

    serverFile = AutoEditorFile(fileName, commentCharacters="#", markerLabel="PRT SSH Server Config")

    if os.path.isfile(fileName):
        log.debug("{} already exists, overwritting autoeditor section...".format(fileName))
        serverFile.addOrReplaceLinesInMarker("NODE", configurationLines)
    else:
        log.debug("{} not found, create new file...".format(fileName))
        pathlib.Path(fileName).touch()
        os.chmod(fileName, 0o600)
        serverFile.addNewMarker("NODE", configurationLines)


# ----------------------------------------------------------------------------------------------------------------------
def removeConfigFileForServer(path: str, name: str) -> None:
    """Removes the SSH config file for a server.

    Args:
        path (str): The path where the SSH config file is stored
        name (str): The name of the server
    """
    if not os.path.isdir(path):
        raise PathNotFound(path)
    os.remove(os.path.join(path, name + ".ptr"))


# ----------------------------------------------------------------------------------------------------------------------
def writeOptimizationOptions(pathToConfigs: str) -> None:
    """Writes the SSH optimiation information to the PRT server directory.

    Args:
        pathToConfigs (str): The path where all the PRT server configurations are stored.
    """
    if not os.path.isdir(pathToConfigs):
        raise PathNotFound(pathToConfigs)

    configurationLines = ["ControlMaster auto",
                          "ControlPath {}/.%n-active".format(pathToConfigs),
                          "ControlPersist 2h",
                          "RemoteForward 32400 127.0.0.1:32400",
                          "RequestTTY force",
                          "LogLevel QUIET"]

    fileName = os.path.join(pathToConfigs, "_.prt")

    serverFile = AutoEditorFile(fileName, commentCharacters="#", markerLabel="PRT SSH Server Config")

    if os.path.isfile(fileName):
        log.debug("{} already exists, overwritting autoeditor section...".format(fileName))
        serverFile.addOrReplaceLinesInMarker("OPTIMIZE", configurationLines)
    else:
        log.debug("{} not found, create new file...".format(fileName))
        pathlib.Path(fileName).touch()
        os.chmod(fileName, 0o600)
        serverFile.addNewMarker("OPTIMIZE", configurationLines)
