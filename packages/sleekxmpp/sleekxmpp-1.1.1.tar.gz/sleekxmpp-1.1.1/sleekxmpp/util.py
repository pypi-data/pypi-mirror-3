# -*- coding: utf-8 -*-
"""
    sleekxmpp.clientxmpp
    ~~~~~~~~~~~~~~~~~~~~

    This module provides common functions and shims for
    importing modules consistently between Python versions.

    Part of SleekXMPP: The Sleek XMPP Library

    :copyright: (c) 2011 Nathanael C. Fritz
    :license: MIT, see LICENSE for more details
"""

import sys


if 'gevent' in sys.modules:
    import gevent.queue as queue
    Queue = queue.JoinableQueue
else:
    try:
        import queue
        Queue = queue.Queue
    except ImportError:
        import Queue as queue
        Queue = queue.Queue


QueueEmpty = queue.Empty
