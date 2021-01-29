"""Module for creating and install systemd override files."""
import logging
import os
import subprocess
import tempfile

from .exceptions import EnvVarNotFoundError
from .exceptions import PathFoundError
from .exceptions import PathNotFound

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

PLEX_SERVICE_FILE = "/lib/systemd/system/plexmediaserver.service"
PLEX_OVERRIDE_DIR = "/etc/systemd/system/plexmediaserver.service.d"
PRT_OVERRIDE_FILE = "10-prt.conf"

scriptBody = """#!/bin/sh
# This script will install an SystemD service override for the plexmediaserver.service

mkdir {overrideDirectory}
echo "[Service]" >> {overrideFile}
echo "Environment=TMPDIR={tempDir}" >> {overrideFile}
echo "Environment=PRT3_CONFIG={configFile}" >> {overrideFile}

systemctl daemon-reload
systemctl systemctl restart plexmediaserver.service
"""


def generateInstallScript(config):
    """Generates an installation script for the systemd override."""
    overrideDirFromConfig = config.getEnvironmentVariable("PLEX_OVERRIDE_DIR")
    overrideFileFromConfig = config.getEnvironmentVariable("PLEX_OVERRIDE_FILE")
    plexServiceFileFromConfig = config.getEnvironmentVariable("PLEX_SERVICE_FILE")
    plexTempDir = config.getEnvironmentVariable("PLEX_MEDIA_SERVER_TMPDIR")

    overrideDir = overrideDirFromConfig if overrideDirFromConfig is not None else PLEX_OVERRIDE_DIR
    overrideFileName = overrideFileFromConfig if overrideFileFromConfig is not None else PRT_OVERRIDE_FILE
    plexServiceFile = plexServiceFileFromConfig if plexServiceFileFromConfig is not None else PLEX_SERVICE_FILE

    if plexTempDir is None:
        raise EnvVarNotFoundError("PLEX_MEDIA_SERVER_TMPDIR")

    plexOverrideFile = os.path.join(overrideDir, overrideFileName)

    if not os.path.isfile(plexServiceFile):
        log.error("Did not find a service file for plexmediaserver!")
        raise PathNotFound(plexServiceFile)

    if os.path.isfile(plexOverrideFile):
        log.error("Founnd a pre-existing override file for PRT!")
        raise PathFoundError(plexOverrideFile)

    return scriptBody.format(overrideDirectory=overrideDir, overrideFile=plexOverrideFile, tempDir=plexTempDir, configFile=config.fileName)


def installSystemdOverride(config):
    """Installs the systemd override."""
    script = generateInstallScript(config)
    log.debug("About it run the following script:")
    log.debug(script)

    with tempfile.TemporaryDirectory() as tempDir:
        installFile = os.path.join(tempDir, "install.sh")

        with open(installFile, "w") as fileHandle:
            fileHandle.write(script)

        command = ["/bin/sh", installFile]
        log.debug("Running this command via subprocess --> {}".format(command))
        response = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response.returncode

    return -1
