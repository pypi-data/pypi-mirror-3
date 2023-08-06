# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2010 Krys Lawrence
#
# Message For You Sir is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# Message For You Sir is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.


"""Tests for m4us.core.messages."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

#---  Third-party imports
import unittest2

#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class MessageShouldProvideIMessage(
  support.ClassShouldProvideAndImplementInterface):

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IMessageFactory,)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IMessage,)


class MessageShouldAcceptKeywordArguments(support.CommonTestBase):

    def test_it_should_set_keyword_arguments_as_attributes(self):
        custom_kwargs = dict(foo='bar', bat='baz')
        kwargs = self._get_required_kwargs()
        kwargs.update(custom_kwargs)
        message = self._call_sut(**custom_kwargs)
        for key, value in kwargs.items():
            self.assert_true(hasattr(message, key))
            self.assert_equal(getattr(message, key), value)


#---  Message tests

class MessageTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import messages
        return messages.Message


class TestMessageShouldImplementIMessage(MessageTestBase,
  MessageShouldProvideIMessage, support.TestCase):

    pass


class TestMessageShouldAcceptKeywordArguments(MessageTestBase,
  MessageShouldAcceptKeywordArguments, support.TestCase):

    pass


#---  Shutdown tests

class ShutdownTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import messages
        return messages.Shutdown


class TestShutdownShouldImplementIMessage(ShutdownTestBase,
  MessageShouldProvideIMessage, support.TestCase):

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        base_interfaces = \
          MessageShouldProvideIMessage._get_result_interfaces(self)
        return base_interfaces + (interfaces.IShutdown,)


class TestShutdownShouldAcceptKeywordArguments(ShutdownTestBase,
  MessageShouldAcceptKeywordArguments, support.TestCase):

    pass


#---  ProducerFinished tests

class ProducerFinishedTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import messages
        return messages.ProducerFinished


class TestProducerFinishedShouldImplementIMessage(ProducerFinishedTestBase,
  MessageShouldProvideIMessage, support.TestCase):

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        base_interfaces = \
          MessageShouldProvideIMessage._get_result_interfaces(self)
        return base_interfaces + (interfaces.IShutdown,
          interfaces.IProducerFinished)


class TestProducerFinishedShouldAcceptKeywordArguments(
  ProducerFinishedTestBase, MessageShouldAcceptKeywordArguments,
  support.TestCase):

    pass


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
