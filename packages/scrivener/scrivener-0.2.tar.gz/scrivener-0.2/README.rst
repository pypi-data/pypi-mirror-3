scrivener: A twisted scribe client/server.
==========================================

scrivener is a Scribe_ client/server framework for use with Twisted_ applications.

Client API
----------

.. code-block:: python

    from twisted.internet import reactor
    from twisted.internet.endpoints import TCP4ClientEndpoint
    from scrivener import ScribeClient


    def main():
        client = ScribeClient(TCP4ClientEndpoint(reactor, '127.0.0.1', 1234))
        client.log('category', 'message1')
        client.log('category', 'message2')

    if __name__ == '__main__':
        reactor.callWhenRunning(main)
        reactor.run()


Server API
----------

.. code-block:: python

    import sys
    from twisted.internet import reactor
    from twisted.internet.endpoints import TCP4ServerEndpoint
    from twisted.python.log import startLogging

    from scrivener import ScribeServerService
    from scrivener.handlers import TwistedLogHandler


    def main():
        service = ScribeServerService(
            TCP4ServerEndpoint(reactor, 1234),
            TwistedLogHandler())
        service.startService()

    if __name__ == '__main__':
        startLogging(sys.stdout)
        reactor.callWhenRunning(main)
        reactor.run()


Server Plugin
-------------

::

    > twistd -n scrivener --help
    Usage: twistd [options] scrivener [scrivener options]
    Options:
      -p, --port=            Port to listen on for scribe service. [default: tcp:0]
      -H, --handlerFactory=  Fully Qualified Name of a callable that returns an
                             ILogHandler
          --version          Display Twisted version and exit.
          --help             Display this help and exit.

    > twistd -n scrivener -p 1234 -H example.MyLogHandler


License
-------
::

    Copyright (C) 2012 Rackspace Hosting, Inc

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.


.. _Scribe: https://github.com/facebook/scribe
.. _Twisted: http://twistedmatrix.com/
