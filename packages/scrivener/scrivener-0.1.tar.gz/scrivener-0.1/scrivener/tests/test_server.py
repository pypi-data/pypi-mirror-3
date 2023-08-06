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

import mock

from zope.interface import directlyProvides

from twisted.trial.unittest import TestCase

from twisted.test.proto_helpers import StringTransport
from twisted.internet.interfaces import IStreamServerEndpoint
from twisted.internet.defer import succeed

from scrivener.interfaces import ILogHandler
from scrivener.server import ScribeServerService


class ScribeServerServiceTests(TestCase):
    def setUp(self):
        self.handler = mock.Mock()
        directlyProvides(self.handler, ILogHandler)

        self.endpoint = mock.Mock()
        directlyProvides(self.endpoint, IStreamServerEndpoint)

        self.port = mock.Mock()

        def _listen(*args, **kwargs):
            return succeed(self.port)

        self.endpoint.listen.side_effect = _listen

        self.service = ScribeServerService(self.endpoint, self.handler)

        self.transport = StringTransport()

    def test_startService(self):
        self.service.startService()
        self.assertEqual(self.endpoint.listen.call_count, 1)

    def test_stopService(self):
        self.service.startService()
        self.service.stopService()

        self.assertEqual(self.port.stopListening.call_count, 1)
