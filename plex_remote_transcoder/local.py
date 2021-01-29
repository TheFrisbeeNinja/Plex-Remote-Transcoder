"""Main file for the PRT local application."""
import logging
from logging.handlers import SysLogHandler
import os
import sys

from plex_remote_transcoder.config.configuration import Configuration

log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(facility=SysLogHandler.LOG_DAEMON, address="/dev/log")
handler.setLevel(logging.DEBUG)
handler.setFormatter(logging.Formatter("prt3-local[%(process)d]: [%(levelname)s] - %(message)s"))
log.addHandler(handler)


# ----------------------------------------------------------------------------------------------------------------------
def main():
    """Entry point for the local transcoder application.

    Configuration and command line tooling is provided by the "prt3" command.
    """
    configFileName = os.environ.get("PRT3_CONFIG")

    if not configFileName:
        log.error("Failed to find PRT3_CONFIG in environment!")
        sys.exit(-1)

    config = Configuration(os.environ.get("PRT3_CONFIG"))

    log.debug(sys.argv)
    sys.exit(-1)
