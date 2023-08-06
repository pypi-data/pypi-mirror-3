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

from twisted.trial.unittest import TestCase

from scrivener.handlers import TwistedLogHandler, CategoryDispatchHandler


class TwistedLogHandlerTests(TestCase):
    @mock.patch('scrivener.handlers.log')
    def test_log(self, mock_log):
        tlh = TwistedLogHandler()

        tlh.log("category", "message")

        mock_log.msg.assert_called_with("message", system="category")


class CategoryDispatchHandlerTests(TestCase):
    def setUp(self):
        self.cdh = CategoryDispatchHandler()

    def test_log(self):
        handler = mock.Mock()

        self.cdh.addHandler('category', handler)
        self.cdh.log('category', 'message')
        handler.log.assert_called_with('category', 'message')

    def test_log_multi_categories(self):
        handler1 = mock.Mock()
        handler2 = mock.Mock()

        self.cdh.addHandler('category1', handler1)
        self.cdh.addHandler('category2', handler2)

        self.cdh.log('category1', 'message')
        handler1.log.assert_called_with('category1', 'message')
        handler2.log.assert_not_called()

        self.cdh.log('category2', 'message')
        handler1.log.assert_not_called()
        handler2.log.assert_called_with('category2', 'message')

    def test_log_multi_handlers(self):
        handler1 = mock.Mock()
        handler2 = mock.Mock()

        self.cdh.addHandler('category', handler1)
        self.cdh.addHandler('category', handler2)

        self.cdh.log('category', 'message')

        handler1.log.assert_called_with('category', 'message')
        handler2.log.assert_called_with('category', 'message')
