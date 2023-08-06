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

from zope.interface import implements

from thrift.protocol import TBinaryProtocol
from thrift.transport import TTwisted

from twisted.python import log
from twisted.application.service import Service

from scrivener._thrift.scribe import ttypes
from scrivener._thrift.scribe import scribe


class _SimpleLogHandler(object):
    implements(scribe.Iface)

    def __init__(self, logHandler):
        self._logHandler = logHandler

    def Log(self, logEntries):
        try:
            for logEntry in logEntries:
                self._logHandler.log(logEntry.category, logEntry.message)

            return ttypes.ResultCode.OK
        except Exception, e:
            log.err(e, "Error handling log entry")
            return ttypes.ResultCode.TRY_LATER


class ScribeServerService(Service):
    def __init__(self, endpoint, handler):
        self._endpoint = endpoint
        self._handler = handler
        self._port = None

    def startService(self):
        if scribe.Iface.providedBy(self._handler):
            handler = self._handler
        else:
            handler = _SimpleLogHandler(self._handler)

        self._processor = scribe.Processor(handler)

        thriftFactory = TTwisted.ThriftServerFactory(
            processor=self._processor,
            iprot_factory=TBinaryProtocol.TBinaryProtocolFactory())

        d = self._endpoint.listen(thriftFactory)

        def _listening(port):
            self._port = port

        d.addCallback(_listening)

    def stopService(self):
        if self._port:
            return self._port.stopListening()
