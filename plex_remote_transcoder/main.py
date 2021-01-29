"""Main file for the PRT application."""
import argparse
import getpass
import logging
import multiprocessing
import os
import sys

import plex_remote_transcoder
from plex_remote_transcoder.config import ssh as SshConfig
from plex_remote_transcoder.config import systemd as Systemd
from plex_remote_transcoder.config.configuration import Configuration
from plex_remote_transcoder.node.server import Server
from plex_remote_transcoder.plex import server as PlexServer
from plex_remote_transcoder.plex import transcoder as PlexTranscoder

log = logging.getLogger()
log.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(message)s"))
log.addHandler(handler)

DEFAULT_CONFIG_FILE = os.path.join(os.environ["HOME"], ".prt3.conf")
DEFAULT_SSH_CONFIG_FILE = os.path.join(os.environ["HOME"], ".ssh", "config")
DEFAULT_NODE_SSH_CONFIG_DIR = os.path.join(os.environ["HOME"], ".ssh", "prt_nodes")


# ----------------------------------------------------------------------------------------------------------------------
def install(arguments) -> int:
    """TODO."""
    if os.path.isfile(arguments.config):
        log.error("For safety, failing to install with a pre-existing configuration file.")
        return -1

    if not os.path.isdir(arguments.workingDir):
        log.error("{} is an invalid working directory!")
        return -1

    if arguments.token is None:
        print("No token provided, attempting to fetch from Plex.tv")
        username = input("Plex Username: ")
        password = getpass.getpass("Plex Password: ")
        arguments.token = PlexServer.fetchAuthToken(username, password)

    conf = Configuration(arguments.config)
    conf.plexAuthToken = arguments.token

    # Setting up the SSH files and saving the vars for later
    log.debug("Installing SSH config files...")
    conf.setEnvironmentVariable("SSH_CONFIG_FILE", arguments.sshConfigFile)
    conf.setEnvironmentVariable("NODE_SSH_CONFIG_DIR", arguments.sshNodeConfigDir)
    SshConfig.installGlobalConfigInclude(arguments.sshConfigFile, arguments.sshNodeConfigDir)
    SshConfig.writeOptimizationOptions(arguments.sshNodeConfigDir)

    # Setting the values for the plex server
    master = Server("plex")
    master.ipAddress = arguments.address
    master.port = arguments.port
    master.user = arguments.user
    conf.master = master

    # Installing the transcoder
    log.debug("Installing transcoders in {}...".format(arguments.transcoderDir))
    conf.setEnvironmentVariable("TRANSCODER_DIR", arguments.transcoderDir)
    PlexTranscoder.installPrtTranscoder(arguments.transcoderDir)

    # Prepping for systemd
    conf.setEnvironmentVariable("PLEX_MEDIA_SERVER_TMPDIR", arguments.workingDir)

    conf.writeToDisk()

    print("TODO: MORE INSTALLATION NEEDS TO GO HERE")
    # Still need the SystemD stuff and the cron stuff
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def checkNodes(arguments) -> int:
    """Pings each node in the configuration file."""
    conf = Configuration(arguments.config)

    if not conf.servers:
        log.info("No servers found in configuration!")
        return 0

    for server in conf.servers:
        result = server.ping()
        log.info("Pinging {} ---> {}".format(server, "PASS" if result else "FAIL"))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def addNode(arguments) -> int:
    """Adds a server to the configuration file."""
    if arguments.name is None:
        log.error("Must provide a NAME when adding a node!")
        return -1

    if arguments.address is None:
        log.error("Must provide an ADDRESS when adding a node!")
        return -1

    newNode = Server(arguments.name)
    newNode.ipAddress = arguments.address
    newNode.port = arguments.port
    newNode.group = arguments.group
    newNode.user = arguments.user

    config = Configuration(arguments.config)
    result = config.addServer(newNode)
    if result:
        config.writeToDisk()
        SshConfig.writeConfigFileForServer(config.getEnvironmentVariable("NODE_SSH_CONFIG_DIR"), newNode)
        log.info("Successfully added node --> {}".format(newNode))
        return 0
    else:
        log.error("Failed to add node {} at {}".format(arguments.name, arguments.address))
        return -1


# ----------------------------------------------------------------------------------------------------------------------
def listNodes(arguments) -> int:
    """Lists all the servers in the configuration file."""
    conf = Configuration(arguments.config)

    if not conf.servers:
        log.info("No servers found in configuration!")

    for server in conf.servers:
        log.info(server)

    return 0


# ----------------------------------------------------------------------------------------------------------------------
def removeNode(arguments) -> int:
    """Removes a server from the configuration file."""
    if arguments.name is None:
        log.error("Must provide a NAME when removing a node!")
        return -1

    config = Configuration(arguments.config)
    wasSuccessful = config.removeServer(arguments.name)
    if wasSuccessful:
        log.info("Server {} successfully removed from config!".format(arguments.name))
        config.writeToDisk()
        SshConfig.removeConfigFileForServer(config.getEnvironmentVariable("NODE_SSH_CONFIG_DIR"), arguments.name)
        return 0
    else:
        log.info("Did not find server {} to remove from config!".format(arguments.name))
    return -1


# ----------------------------------------------------------------------------------------------------------------------
def getLoad(arguments) -> int:
    """Returns the normalized CPU load of the local machine."""
    numberOfProcessors = multiprocessing.cpu_count()
    loadData = os.getloadavg()
    normalizedLoad = [int(load / numberOfProcessors * 100) for load in loadData]
    log.info("{} {} {}".format(*normalizedLoad))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def getClusterLoad(arguments) -> int:
    """Lists all the servers in the configuration file."""
    conf = Configuration(arguments.config)

    if not conf.servers:
        log.info("No servers found in configuration!")

    for server in conf.servers:
        returnCode, load = server.getLoad()
        log.info("{} --> {}".format(server, "{} {} {}".format(*load) if returnCode == 0 else "Failed to fetch load data"))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def installSystemd(arguments) -> int:
    """Attemps to install the systemd override file."""
    if not os.path.isfile(arguments.config):
        log.error("Must specify a valid configuration file!")
        return -1

    conf = Configuration(arguments.config)

    if os.geteuid() == 0:
        log.info("About to run the install script...\n\n")
        while True:
            reply = str(input("Run above script as root? (y/n): ")).lower().strip()
            if reply[:1] == "y":
                break
            if reply[:1] == "n":
                return -1

        return Systemd.installSystemdOverride(conf)

    else:
        log.info("SystemD modifications must be done as root. You have two options:")
        log.info("\n 1) Run the following command:")
        log.info("\n       sudo prt3 --config {} install-systemd".format(arguments.config))
        log.info("\n\n 2) Copy and paste the following commands and run them as root yourself:\n")
        log.info(Systemd.generateInstallScript(conf))
    return 0


# ----------------------------------------------------------------------------------------------------------------------
def _buildArgParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG_FILE, help="Configuration file")
    parser.add_argument("-v", "--version", action="version", version=plex_remote_transcoder.VERSION)
    parser.add_argument("--verbose", action="store_true", help="Turns on ALL the prints!")

    subParsers = parser.add_subparsers(help='PRT operation to perform', required=True, dest='cmd')

    installParser = subParsers.add_parser('install', help='Install PRT for the first time')
    installParser.set_defaults(func=install)
    installParser.add_argument("-p", "--port", help="Port the Plex server is listening on", default=32400)
    installParser.add_argument("-a", "--address", help="Address of the Plex server", default="127.0.0.1")
    installParser.add_argument("-u", "--user", help="User the plex server is running as", default="plex")
    installParser.add_argument("-t", "--token", help="Plex authorization token")
    installParser.add_argument("--sshConfigFile", help="The global SSH config file", default=DEFAULT_SSH_CONFIG_FILE)
    installParser.add_argument("--sshNodeConfigDir", help="Directory to story node SSH config files", default=DEFAULT_NODE_SSH_CONFIG_DIR)
    installParser.add_argument("--transcoderDir", help="Directory where the Plex transcoders are installed", default=PlexTranscoder.DEFAULT_TRANSCODER_DIR)
    installParser.add_argument("--workingDir", help="Directory where Plex will story temp transcode output", required=True)

    checkNodesParser = subParsers.add_parser('check-nodes', help='Checks the nodes with a basic SSH ping')
    checkNodesParser.set_defaults(func=checkNodes)

    getLoadParser = subParsers.add_parser('get-load', help='Returns the server load')
    getLoadParser.set_defaults(func=getLoad)

    listNodesParser = subParsers.add_parser('list-nodes', help='Lists all the nodes in config')
    listNodesParser.set_defaults(func=listNodes)

    addNodeParser = subParsers.add_parser('add-node', help='Adds a new node to the config')
    addNodeParser.set_defaults(func=addNode)
    addNodeParser.add_argument("-n", "--name", help="Name of the new node")
    addNodeParser.add_argument("-u", "--user", help="User to login as on the node", default="plex")
    addNodeParser.add_argument("-p", "--port", help="Port to connect to on the node", default=22)
    addNodeParser.add_argument("-a", "--address", help="Address of the node")
    addNodeParser.add_argument("-g", "--group", help="Group the node belongs to", default="default")

    removeNodeParser = subParsers.add_parser("remove-node", help="Removes a node from the config")
    removeNodeParser.set_defaults(func=removeNode)
    removeNodeParser.add_argument("-n", "--name", help="Name of the new node")

    getClusterLoadParser = subParsers.add_parser("get-cluster-load", help="Displays the CPU load of the cluster")
    getClusterLoadParser.set_defaults(func=getClusterLoad)

    installSystemdParser = subParsers.add_parser("install-systemd", help="Installs systemd overrides")
    installSystemdParser.set_defaults(func=installSystemd)

    return parser


# ----------------------------------------------------------------------------------------------------------------------
def main():
    """Main entry point for the 'prt3' tool."""
    parser = _buildArgParser()
    arguments = parser.parse_args()
    if arguments.verbose:
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("[%(asctime)s] [%(filename)s:%(lineno)s] [%(levelname)s] - %(message)s"))
    sys.exit(arguments.func(arguments))
