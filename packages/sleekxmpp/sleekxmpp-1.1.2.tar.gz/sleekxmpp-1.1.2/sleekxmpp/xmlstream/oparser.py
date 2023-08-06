# -*- encoding: utf-8 -*-

"""
    sleekxmpp.xmlstream.parser
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    This module provides a customized XML parser that restricts
    the use of certain XML features as mandated by RFC 6120.

    Part of SleekXMPP: The Sleek XMPP Library

    :copyright: (c) 2012 Nathanael C. Fritz
    :license: MIT, see LICENSE for more details
"""

# pylint: disable-msg=W0613,R0201

from sleekxmpp.xmlstream import ET


class RestrictedXMLError(Exception):
    """Raised if a restricted XML feature is detected.
    
    Restrictions include: comments, doctypes, processing instructions,
    and entity references beyond the basic five (for &, <, >, ", and ').

    .. warning::
        
        If using a Python version before 3.3, detection of doctypes and
        additional entity references can not be guaranteed.
    """


class StreamReader(object):

    """
    Convert parsing events into XML objects.

    In order to conserve memory dealing with an XML stream,
    top level child elements are passed to a callback instead
    of being appended to the root XML object.

    :param func stream_start: Called when the opening tag of the
                              stream root is found.
    :param func stream_end: Called when the root closing tag is
                            received.
    :param func child_recv: Called when a top-level child has
                            been parsed.

    All three callbacks (`stream_start`, `stream_end`, and
    `child_recv` accept a single parameter, which is the
    constuctued :class:`~xml.etree.Element` object for the
    parsed XML.
    """

    # pylint: disable-msg=R0902

    def __init__(self, stream_start=None, stream_end=None, child_recv=None):
        self.root = None
        self.depth = 0
        self.buffer = []
        self.prev = None
        self.tail = None
        self.stack = []

        null_cb = lambda x: None

        self.stream_start = stream_start or null_cb
        self.stream_end = stream_end or null_cb
        self.child_recv = child_recv or null_cb

    def close(self):
        """Finish processing parse events."""
        return self.root

    def data(self, data):
        """Buffer text data for the current XML object."""
        self.buffer.append(data)

    def end(self, tag):
        """Finish building an XML object."""
        self._flush_text()
        if self.stack:
            self.prev = self.stack.pop()
        else:
            self.prev = self.root
        self.tail = True
        self.depth -= 1

        assert tag == self.prev.tag, \
               'end tag mismatch (expected %s, got %s)' % (
                       self.prev.tag, tag)

        if self.depth == 0:
            self.stream_end(self.root)
        elif self.depth == 1:
            self.child_recv(self.prev)

        return self.prev

    def start(self, tag, attrs):
        """Start building a new XML object."""
        self._flush_text()
        self.prev = elem = ET.Element(tag, attrs)
        self.tail = False

        if self.depth == 0:
            self.root = elem
            self.stack = []
            self.stream_start(self.root)
        else:
            if self.stack:
                self.stack[-1].append(elem)
            self.stack.append(elem)

        self.depth += 1
        return elem

    def _flush_text(self):
        """Combine text and append it to the current XML object."""
        if self.buffer:
            if self.prev is not None:
                text = ''.join(self.buffer)
                if self.tail:
                    self.prev.tail = text
                else:
                    self.prev.text = text
            self.buffer = []

    def pi(self, *args):
        """Prevent executing processing instructions."""
        raise RestrictedXMLError("Processing instructions are prohibited.")

    def doctype(self, *args):
        """Prevent loading DTDs.

        .. warning::

            It turns out that cElementTree does not use this method until
            Python3.3, contrary to the claims of the documentation. So do
            not depend on catching doctype related security attacks (which
            include entity definitions, like the Billion Laughs attack) if
            using Python2.6 through Python3.2.
        """
        raise RestrictedXMLError("Doctypes are prohibited.")

    def comment(self, *args):
        """Deny the use of XML comments, as they are not needed."""
        raise RestrictedXMLError("XML comments are prohibited.")
