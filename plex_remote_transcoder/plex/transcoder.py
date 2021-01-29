"""Module for working with the transcoders in Plex.

In this file we handle three named transcoders. The first is the "PLEX" transcoder. This is what is installed by
the Plex Media Installer. It's a Plex customized build of ffmpeg.

The second is the "LOCAL" transcoder. This is just the Plex transcoder renamed. We will invoke this transcoder when
we want the local machine to perform the transcode.

The third is the "REMOTE" transcoder. This is our program which will forward our transcode operation to one of the
nodes (which will then use the "LOCAL" transcoder) for processing.
"""
import logging
import os
import shutil

from .exceptions import LocalTranscoderFoundError
from .exceptions import RemoteTranscoderExeNotFoundError
from .exceptions import RemoteTranscoderFoundError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

DEFAULT_TRANSCODER_DIR = "/usr/lib/plexmediaserver"
PLEX_TRANSCODER_NAME = "Plex Transcoder"
REMOTE_TRANSCODER_NAME = "prt_remote_transcoder"
LOCAL_TRANSCODER_NAME = "prt_local_transcoder"


# ----------------------------------------------------------------------------------------------------------------------
def installPrtTranscoder(directory: str) -> None:
    """Installs the remote transcoder into the Plex installation.

    Args:
        directory (str): Directory where the Plex transcoders are installed."
    """
    remoteExec = shutil.which("prt3-remote")
    if not remoteExec:
        log.error("Could not find the 'prt3-remote' executable!")
        raise RemoteTranscoderExeNotFoundError()

    originalTranscoder = os.path.join(directory, PLEX_TRANSCODER_NAME)
    localTranscoder = os.path.join(directory, LOCAL_TRANSCODER_NAME)
    remoteTranscoder = os.path.join(directory, REMOTE_TRANSCODER_NAME)

    if os.path.isfile(localTranscoder):
        log.error("Local transcoder already exists at {}, not proceeding!".format(localTranscoder))
        raise LocalTranscoderFoundError(localTranscoder)

    if os.path.isfile(remoteTranscoder):
        log.error("Remote transcoder already exists at {}, not proceeding!".format(remoteTranscoder))
        raise RemoteTranscoderFoundError(remoteTranscoder)

    # The original, ffmpeg-based transcoder that ships with Plex becomes our local transcoder
    os.rename(originalTranscoder, localTranscoder)

    # The prt3-remote program becomes our remote transcoder
    shutil.copyfile(remoteExec, os.path.join(directory, remoteTranscoder))
    os.chmod(remoteTranscoder, 0o755)

    # Install a symlink, so that the Plex Media Server installation calls our remote transcoder
    os.symlink(remoteTranscoder, originalTranscoder)
