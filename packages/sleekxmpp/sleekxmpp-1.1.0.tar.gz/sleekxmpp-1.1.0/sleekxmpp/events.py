# -*- encoding: utf-8 -*-

"""
    sleekxmpp.events
    ~~~~~~~~~~~~~~~~

    Part of SleekXMPP: The Sleek XMPP Library
    :copyright: (c) 2012 Nathanael C. Fritz
    :license: MIT, see LICENSE for more details
"""

import logging
import threading
import copy

from collections import namedtuple

from sleekxmpp.util import Queue, QueueEmpty


log = logging.getLogger(__name__)


Event = namedtuple('Event', ['name', 'handler', 'data', 'exception'])
Handler = namedtuple('Handler', ['id', 'func', 'threaded', 'once'])


def _run_event(event):
    try:
        event.handler.func(event.data)
    except Exception as e:
        if event.exception:
            event.exception(e)
        else:
            error_msg = 'Error processing event handler: %s'
            log.exception(error_msg,  str(event.handler.func))


def run_event(event):
    if event.handler.threaded:
        threading.Thread(
            name='Event_%s_%s' % (event.name,
                                  event.handler.func),
            target=_run_event,
            args=(event,)).start()
    else:
        _run_event(event)


class RepeatableTimer(threading.Thread):

    def __init__(self, stop, interval, function, repeat=False, 
                 args=None, kwargs=None):
        threading.Thread.__init__(self)
        self.interval = interval
        self.function = function
        self.repeat = repeat
        self.finished = stop

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        self.kwargs = kwargs

    def cancel(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()

    def run(self):
        while not self.finished.is_set() and self.repeat:
            elapsed = 0
            while elapsed < self.interval and not self.finished.is_set():
                self.finished.wait(0.1)
                elapsed += 0.1
                if elapsed >= self.interval:
                    if not self.finished.is_set():
                        self.function(*self.args, **self.kwargs)
                    if not self.repeat:
                        self.finished.set()


class EventLoop(object):

    def __init__(self, stop, config=None):
        self.handler_lock = threading.Lock()
        self.handler_id_lock = threading.Lock()

        self.__next_id = 0
        self.timeout = 1
        self.event_handlers = {}
        self.event_queue = Queue()

        self.scheduled_events = {}

        self.finished = stop

    def _next_id(self):
        with self.handler_id_lock:
            self.__next_id += 1
            return self.__next_id

    def on(self, name, func, threaded=False, once=False):
        with self.handler_lock:
            handler = Handler(self._next_id(), func, threaded, once)
            if name not in self.event_handlers:
                self.event_handlers[name] = {}
            self.event_handlers[name][handler.id] = handler

    def schedule(self, name, func, interval, 
                 repeat=False, args=None, kwargs=None):
        self.scheduled_events[name] = RepeatableTimer(
                self.finished,
                interval,
                func,
                repeat=repeat,
                args=args,
                kwargs=kwargs)
        self.scheduled_events[name].start()

    def remove(self, name, func):
        with self.handler_lock:
            handlers = self.event_handlers.get(name, {})
            self.event_handlers[name] = dict(
                (id, handler) for id, handler in handlers.items() \
                        if handler.func != func)

    def cancel(self, name):
        if name in self.scheduled_events:
            self.scheduled_events[name].cancel()

    def clear(self, name):
        self.event_handlers[name] = {}

    def handled(self, name):
        return len(self.event_handlers.get(name, {}))

    def handlers(self, name):
        return self.event_handlers.get(name, {})

    def emit(self, name, data, direct=False):
        discarded_handlers = set()

        handlers = self.event_handlers.get(name, {})
        for handler_id in handlers:
            handler = handlers[handler_id]

            exception = getattr(data, 'exception', None)
            event = Event(name, handler, copy.copy(data), exception)
            if direct:
                run_event(event)
            else:
                self.event_queue.put(event)
            if event.handler.once:
                discarded_handlers.add(handler_id)

        with self.handler_lock:
            for handler in discarded_handlers:
                if handler in self.event_handlers[name]:
                    del self.event_handlers[name][handler]

    def process(self):
        log.debug('Starting event loop processor.')
        while not self.finished.is_set():
            try:
                event = self.event_queue.get(True, timeout=self.timeout)
            except QueueEmpty:
                continue
            run_event(event)
        log.debug('Stopped event loop processor.')

    def stop(self):
        self.finished.set()
        for timer in self.scheduled_events:
            self.scheduled_events[timer].cancel()
