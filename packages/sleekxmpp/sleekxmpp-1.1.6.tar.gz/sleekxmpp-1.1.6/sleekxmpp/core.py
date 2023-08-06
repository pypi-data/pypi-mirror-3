import threading

from sleekxmpp.events import EventLoop
from sleekxmpp.api import APIRegistry
from sleekxmpp.plugins.base import PluginManager


class XMPP(object):

    def __init__(self, jid, settings=None):
        self.settings = settings if settings else {}
        self.credentials = {}

        self.api = APIRegistry()
        self.events = EventLoop()
        self.plugins = PluginManager(self, self.settings)

        self.stop = threading.Event()

        self.bindings = {}

        self.jid = None
        self.streams = {}
    
        self.plugins.enable('rfc_6120')
        self.plugins.enable('rfc_6121')
        self.plugins.enable('rfc_6122')
