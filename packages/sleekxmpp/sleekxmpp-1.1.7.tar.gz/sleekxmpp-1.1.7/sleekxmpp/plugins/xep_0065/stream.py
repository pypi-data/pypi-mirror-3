class SOCKS5Stream(object):

    def __init__(self, xmpp, sid, to, ifrom, proxy=None, port=None):
        self.xmpp = xmpp
        self.sid = sid
        self.receiver = to
        self.sender = ifrom
        self.proxy = proxy

        self.stream_started = threading.Event()

    def connect(self):
        self.socket = socksocket()
        self.socket.setproxy(PROXY_TYPE_SOCKS5, self.proxy, port=self.port)

    def activate(self, block=True, timeout=None, callback=None):
        host = self.
