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

from twisted.python import usage

from twisted.internet import reactor
from twisted.internet.endpoints import serverFromString
from twisted.python.reflect import namedAny

from scrivener.handlers import TwistedLogHandler
from scrivener.server import ScribeServerService


class Options(usage.Options):
    synopsis = "[scrivener options]"
    optParameters = [
        ["port", "p", "tcp:0",
            "Port to listen on for scribe service."],
        ["handlerFactory", "H", None,
            "Fully Qualified Name of a callable that returns an ILogHandler"]]


def makeService(config):
    endpoint = serverFromString(reactor, config['port'])
    if config['handlerFactory'] is None:
        handlerFactory = TwistedLogHandler
    else:
        handlerFactory = namedAny(config['handlerFactory'])

    return ScribeServerService(endpoint, handlerFactory())
