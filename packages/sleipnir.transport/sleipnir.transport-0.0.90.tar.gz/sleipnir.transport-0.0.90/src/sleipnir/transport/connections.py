#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""
Connections

Represents a generic gateway to AMQP implementation
"""

from __future__ import absolute_import

__author__  = "Carlos Martin <cmartin@liberalia.net>"
__license__ = "See LICENSE file for details"

# Import here any required modules.
from functools import partial

from pika import PlainCredentials, ConnectionParameters
from pika.adapters import SelectConnection

__all__ = ['ConnectionFactory']

# Project requirements
from sleipnir.core.factory import NamedAbstractFactory

# local submodule requirements
from .enums import ConnectionType, ConnectionState
from .pools import ChannelPool, BuilderPool
from .parser import connection_url, URI


BACKPRESSURE = 0.15
BACKPRESSURE_LIMIT = 90
BACKPRESSURE_MULTIPLIER = 3


class ConnectionError(Exception):
    """Connection exception"""


class ConnectionFactory(NamedAbstractFactory):
    """Connection factory"""

    _shared_backends = {}
    _shared_connections = {}

    def __init__(self):
        super(ConnectionFactory, self).__init__()
        self._last = []
        self._default = None

    def __getattribute__(self, name):
        if name == '_backends':
            name = '_shared_backends'
        if name == '_connections':
            name = '_shared_connections'
        return object.__getattribute__(self, name)

    def __getitem__(self, key):
        return self._connections.get(key, None)

    def __delitem__(self, key):
        if key in self._connections:
            self._connections[key].close()
        del self._connections[key]

    def _on_connected(self, conn):
        conn.state = ConnectionState.STARTED
        if conn.url in self._connections:
            # Set default conn if no one has been set
            self._default = self._default or conn
            self._last.append(conn)
            # invoke template method
            self.when_connected(conn)
            # add callbacks for close and backpressure events
            conn.add_on_close_callback(self._on_disconnected)
            conn.add_backpressure_callback(self._on_backpressure)

    def _on_disconnected(self, conn):
        conn.state = ConnectionState.CLOSED
        if conn.url in self._connections:
            self.when_disconnected(conn)
            self._last.remove(conn)

    def _on_backpressure(self, conn):
        if conn.url in self._connections:
            if not conn.push_timeout:
                conn.push_timeout = BACKPRESSURE
            conn.push_timeout *= BACKPRESSURE_MULTIPLIER
            conn.push_timeout = min(conn.push_timeout, BACKPRESSURE_LIMIT)
            # notify about pressure
            self.when_backpressure(conn)

    def _on_connection_timeout(self):
        for conn in self._connections.values():
            if conn.state == ConnectionState.STARTING:
                self.when_error(conn)
                del self._connections[conn.url]

    def when_connected(self, connection):
        pass

    def when_disconnected(self, connection):
        pass

    def when_backpressure(self, connection):
        pass

    def when_error(self, connection):
        pass

    @property
    def default(self):
        if not self._default:
            for conn in self._connections.itervalues():
                return conn
        return self._default

    @property
    def last(self):
        return self._last[-1] if self._last else None

    def create(self, url, conn_type=ConnectionType.ASYNC):
        # check that url pased (url_string, connection or channel)
        # doesn't exist in connections pool
        connection = url
        if hasattr(connection, 'slp_connection'):
            connection = url.slp_connection
        if isinstance(connection, AbstractConnection):
            url = connection.url

        # check now url
        if url not in self._connections:
            conn = super(ConnectionFactory, self).create(url, conn_type)
            self._connections[url] = conn
            # set callbacks
            conn.add_on_open_callback(self._on_connected)
            # add a timeout so if connection isn't valid, we should remove it
            conn.add_timeout(2, self._on_connection_timeout)
            conn.state = ConnectionState.STARTING
        return self._connections[url]


class MetaConnection(type):
    """Connection Metaclass"""

    def __init__(mcs, name, bases, dct):
        type.__init__(mcs, name, bases, dct)
        if not name.endswith("Connection"):
            ConnectionFactory.get_instance().register(name, mcs)


class AbstractConnection(object):
    """Prepares a connection. only get a pika connection is lazy created"""

    __metaclass__ = MetaConnection

    def __init__(self, url, limit=4):
        """Whenever a property changes, update stamp"""
        self._url = URI(url, connection_url)
        self._state = ConnectionState.CLOSED
        self._push_timeout = 0
        # set up pools
        self._builders_pool = BuilderPool(self)
        self._channels_pool = ChannelPool(self, limit)

    @property
    def type(self):
        return self.CONNECTION_TYPE

    @property
    def url(self):
        return str(self._url)

    @property
    def channels(self):
        return self._channels_pool

    @property
    def builders(self):
        return self._builders_pool

    @property
    def loop(self):
        # get connection variable to be used by start method
        connection = self

        def start(self, timeout=None):
            if timeout is not None:
                connection.add_timeout(timeout, connection.close)
            return self.__class__.start(self)

        # Start event loop
        if not hasattr(self.ioloop, "slp_monkey_patched"):
            self.ioloop.slp_monkey_patched = True
            klass = self.ioloop.__class__
            func_type = type(klass.start)
            self.ioloop.start = func_type(start, self.ioloop, klass)
        return self.ioloop

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    @property
    def push_timeout(self):
        return self._push_timeout

    @push_timeout.setter
    def push_timeout(self, value):
        self._push_timeout = value

    def wait(self, state, callback):
        if state == self._state:
            return callback(self)
        if state == ConnectionState.STARTED:
            return self.add_on_open_callback(callback)
        if state == ConnectionState.CLOSED:
            return self.add_on_close_callback(callback)

        # Unsupported State
        raise NotImplementedError

    def routes(self, builder, **builder_kwargs):
        builder = builder(self, **builder_kwargs)
        return self._builders_pool.register(builder)

    @classmethod
    def can_handle(cls, url, conn_type):
        return cls.CONNECTION_TYPE == conn_type

    @classmethod
    def new(cls, url, conn_type):
        return cls(url)


class ConnectionMock(AbstractConnection):
    """A mock connection object"""

    CONNECTION_TYPE = ConnectionType.MOCK

    class IOLoopMock(object):
        def start(self):
            pass

    @property
    def loop(self):
        return IOLoopMock()


class PikaConnection(AbstractConnection):

    def __init__(self, url):
        AbstractConnection.__init__(self, url)

        credentials = None
        if self._url.username:
            credentials = PlainCredentials(
                self._url.username, self._url.password)

        for host, port in self._url.hosts():
            self._parameters = ConnectionParameters(
                credentials=credentials,
                host=host,
                port=port,
                virtual_host=self._url.vhost)

            #Fixme: Support multiple hosts
            break


class ConnectionAsync(PikaConnection, SelectConnection):

    CONNECTION_TYPE = ConnectionType.ASYNC

    def __init__(self, url):
        PikaConnection.__init__(self, url)
        SelectConnection.__init__(self, self._parameters)
