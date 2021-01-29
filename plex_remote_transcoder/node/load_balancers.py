"""Load balancers for chosing which node to use."""
import logging
from typing import List

from .server import Server

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def selectServerViaStrategy(servers: List[Server], strategy: str) -> Server:
    """Returns a node to begin a new transcode on based on the provided strategy.

    Args:
        servers (List[Server]): Servers to chose from
        strategy (str): The strategy to use
    """
    if strategy == "minimumLoad":
        return getServerWithMinLoad(servers)

    log.error("Invalid loadBalanceStrategy --> {}".format(strategy))
    return None


def getServerWithMinLoad(servers: List[Server]) -> Server:
    """Returns the server with the minimum CPU load.

    Args:
        servers (List[Server]): Server to choose from.
    """
    minLoadedServer = None
    minLoad = []

    for server in servers:
        response, load = server.getLoad()

        if response != 0:
            continue

        if not minLoad or minLoad[0] > load[0]:
            minLoadedServer = server
            minLoad = load

    return minLoadedServer
