"""
devices.py

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

import requests
from xml.etree import ElementTree as etree

from .nodes import Description
from .exceptions import FritzConnectionException


def get_content_from(url):
    conn = requests.get(url)
    ct = conn.headers.get("Content-type")
    if ct == "text/html":
        raise FritzConnectionException("Unable to login into device to get configuration information.")
    return conn.text


class DeviceManager:
    """
    Knows all data about the device and the sub-devices, including the
    available services.
    """

    def __init__(self):
        self.descriptions = []
        self.services = {}

    @property
    def modelname(self):
        """
        Take the root-device of the first description and return the
        according modelname. This is the name of the Fritz!Box itself.
        Will raise an IndexError if the method is called before
        descriptions are added.
        """
        return self.descriptions[0].device_model_name

    def add_description(self, source):
        """
        Adds description data about the devices and the according
        services. 'source' is a string with the xml-data, like the
        content of an igddesc- or tr64desc-file.
        """
        if isinstance(source, str):
            if source.startswith("http://") or source.startswith("https://"):
                source = get_content_from(source)
        tree = etree.parse(source)
        root = tree.getroot()
        self.descriptions.append(Description(root))

    def scan(self):
        """
        Scans all available services defined by the description files.
        Must get called after all xml-descriptions are added.
        """
        for description in self.descriptions:
            self.services.update(description.services)

    def load_service_descriptions(self, address, port):
        """
        Triggers the load of the scpd files of the services, so they
        known their actions.
        """
        for service in self.services.values():
            service.load_scpd(address, port)

