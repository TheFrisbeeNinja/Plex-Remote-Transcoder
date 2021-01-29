"""Simple helper classes for parsing the XML data from Plex."""
import logging
from typing import List

from lxml import etree

from .exceptions import XmlTagMismatchError

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# ----------------------------------------------------------------------------------------------------------------------
class Session(object):
    """Plex API defined session."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["id"] = xmlData.get("id")
        self._data["bandwidth"] = xmlData.get("bandwidth")
        self._data["location"] = xmlData.get("location")

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def sessionId(self):
        """The id of the session."""
        return self._data["id"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def bandwidth(self):
        """Bandwidth assigned to the session."""
        return self._data["bandwidth"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def location(self):
        """Location of the session."""
        return self._data["location"]


# ----------------------------------------------------------------------------------------------------------------------
class TranscodeSession(object):
    """Plex API defined transcode session."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["key"] = xmlData.get("key")
        self._data["videoDecision"] = xmlData.get("videoDecision")
        self._data["audioDecision"] = xmlData.get("audioDecicion")
        self._data["videoCodec"] = xmlData.get("videoCodec")
        self._data["audioCodec"] = xmlData.get("audioCodec")
        self._data["transcodeHwRequested"] = xmlData.get("transcodeHwRequested")
        self._data["transcodeHwFullPipeline"] = xmlData.get("transcodeHwFullPipeline")

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def key(self):
        """The key for the transcode session."""
        return self._data["key"]


# ----------------------------------------------------------------------------------------------------------------------
class Player(object):
    """Plex API defined player."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData=None):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["address"] = xmlData.get("address")

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def address(self):
        """The address of the player."""
        return self._data["address"]


# ----------------------------------------------------------------------------------------------------------------------
class User(object):
    """Plex API defined user."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData=None):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["id"] = xmlData.get("id")
        self._data["name"] = xmlData.get("title")

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def name(self):
        """The name of the user."""
        return self._data["name"]


# ----------------------------------------------------------------------------------------------------------------------
class Media(object):
    """Plex API defined media."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData=None):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["id"] = xmlData.get("id")

        for child in xmlData:
            if child.tag == "Part":
                self._data["part"] = Part(child)

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def part(self):
        """The part object for this media object."""
        return self._data["part"]


# ----------------------------------------------------------------------------------------------------------------------
class Part(object):
    """Plex API defined part."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}
        self._data["streams"] = []

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["id"] = xmlData.get("id")
        self._data["protocol"] = xmlData.get("protocol")
        self._data["decision"] = xmlData.get("decision")

        for child in xmlData:
            if child.tag == "Stream":
                self._data["streams"].append(Stream(child))

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def streams(self):
        """Stream objects for this part."""
        return self._data["streams"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def protocol(self):
        """The protocol this part is using."""
        return self._data["protocol"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def decision(self):
        """The decision made for this part by the server."""
        return self._data["decision"]


# ----------------------------------------------------------------------------------------------------------------------
class Stream(object):
    """Plex API defined stream."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData=None):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["decision"] = xmlData.get("decision")
        self._data["location"] = xmlData.get("location")
        self._data["codec"] = xmlData.get("codec")

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def decision(self):
        """The decision the server made for this stream."""
        return self._data["decision"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def location(self):
        """The location of the stream."""
        return self._data["location"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def codec(self):
        """The codec being used by the stream."""
        return self._data["codec"]


# ----------------------------------------------------------------------------------------------------------------------
class Video(object):
    """Plex API defined stream."""
    # ------------------------------------------------------------------------------------------------------------------
    def __init__(self, xmlData=None):
        """Initializes the object from XML data.

        Args:
            xmlData (etree): XML data to use.
        """
        self._data = {}

        if xmlData.tag != self.__class__.__name__:
            raise XmlTagMismatchError(desiredTag=self.__class__.__name__, foundTag=xmlData.tag)

        self._data["key"] = xmlData.get("key")
        self._data["type"] = xmlData.get("type")

        for child in xmlData:
            if child.tag == "Media":
                self._data["media"] = Media(child)
            elif child.tag == "Session":
                self._data["session"] = Session(child)
            elif child.tag == "TranscodeSession":
                self._data["transcodeSession"] = TranscodeSession(child)
            elif child.tag == "Player":
                self._data["player"] = Player(child)
            elif child.tag == "User":
                self._data["user"] = User(child)
            else:
                pass

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def key(self):
        """Key for this video."""
        return self._data["key"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def mediaType(self):
        """The type of media."""
        return self._data["type"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def media(self):
        """The media object."""
        return self._data["media"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def sessions(self):
        """The session object."""
        return self._data["session"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def transcodeSession(self):
        """The transcode session object."""
        return self._data["transcodeSession"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def player(self):
        """The player object."""
        return self._data["player"]

    # ------------------------------------------------------------------------------------------------------------------
    @property
    def user(self):
        """The user object."""
        return self._data["user"]


# ----------------------------------------------------------------------------------------------------------------------
def parseXml(data: str) -> List[Video]:
    """Parses an XML string for Plex XML data.

    Args:
        data (str): XML data in string form.
    """
    xml = etree.fromstring(data)
    videos = []

    if xml.tag != "MediaContainer":
        raise XmlTagMismatchError(desiredTag="MediatContainer", foundTag=xml.tag)

    log.debug("XML data has {} elements".format(xml.get("size")))

    for child in xml:
        if child.tag == "Video":
            videos.append(Video(child))
    return videos
