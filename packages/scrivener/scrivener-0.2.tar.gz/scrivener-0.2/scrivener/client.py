# Copyright 2012 Rackspace Hosting, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from thrift.transport import TTwisted
from thrift.protocol import TBinaryProtocol

from twisted.python import log

from twisted.internet.protocol import Factory, Protocol
from twisted.internet.defer import Deferred, succeed

from scrivener._thrift.scribe import scribe
from scrivener._thrift.scribe import ttypes


class _LossNotifyingWrapperProtocol(Protocol):
    def __init__(self, wrapped, on_connectionLost):
        self.wrapped = wrapped
        self._on_connectionLost = on_connectionLost

    def dataReceived(self, data):
        self.wrapped.dataReceived(data)

    def connectionLost(self, reason):
        self.wrapped.connectionLost(reason)
        self._on_connectionLost(reason)

    def connectionMade(self):
        self.wrapped.makeConnection(self.transport)


class _ThriftClientFactory(Factory):
    def __init__(self, client_class, on_connectionLost):
        self._client_class = client_class
        self._on_connectionLost = on_connectionLost

    def buildProtocol(self, addr):
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        p = TTwisted.ThriftClientProtocol(self._client_class, pfactory)

        wrapper = _LossNotifyingWrapperProtocol(
            p, self._on_connectionLost)

        return wrapper


class ScribeClient(object):
    _state = 'NOT_CONNECTED'

    def __init__(self, scribe_endpoint):
        self._scribe_endpoint = scribe_endpoint
        self._client_factory = _ThriftClientFactory(
            scribe.Client,
            self._connection_lost)
        self._client = None
        self._waiting = []

    def _notify_connected(self):
        d = Deferred()
        self._waiting.append(d)
        return d

    def _connection_made(self, client):
        self._state = 'CONNECTED'
        self._client = client.wrapped
        while self._waiting:
            d = self._waiting.pop(0)
            d.callback(self._client)
        return self._client

    def _connection_lost(self, reason):
        self._state = 'NOT_CONNECTED'
        self._client = None
        log.err(
            reason,
            "Connection lost to scribe server: {0}".format(
                self._scribe_endpoint))

    def _connection_failed(self, reason):
        self._state = 'NOT_CONNECTED'
        self._client = None
        log.err(
            reason,
            "Could not connect to scribe server: {0}".format(
                self._scribe_endpoint))

    def _get_client(self):
        if self._state == 'NOT_CONNECTED':
            self._state = 'CONNECTING'
            d = self._scribe_endpoint.connect(self._client_factory)
            d.addCallbacks(self._connection_made, self._connection_failed)
            return d
        elif self._state == 'CONNECTING':
            return self._notify_connected()
        elif self._state == 'CONNECTED':
            return succeed(self._client)

    def log(self, category, messages):
        if isinstance(messages, basestring):
            messages = [messages]

        entries = [ttypes.LogEntry(category, message) for message in messages]

        def _log(client):
            return client.client.Log(entries)

        d = self._get_client()
        d.addCallback(_log)
        return d
