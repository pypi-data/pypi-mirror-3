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


"""Tests for m4us.backplanes."""


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
import mock

#---  Project imports
from m4us.core.tests import (test_components, test_coroutines, test_exceptions,
  test_messages, support)


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class PublisherKwargsMixin(object):

    def _get_required_kwargs(self):
        return dict(publisher='some publisher')


class ShutdownMessageMixin(object):

    # We do not want a new implementations, just a new locations.
    __source_class = test_coroutines.CoroutineShouldRespondToShutdownMessages
    _make_shutdown_message = __source_class._make_shutdown_message.__func__
    _get_ishutdown_interface = __source_class._get_ishutdown_interface.__func__


#---  RegisterPublisher tests

class RegisterPublisherTestBase(PublisherKwargsMixin, support.CommonTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.RegisterPublisher


class TestRegisterPublisherShouldProvideInterfaces(RegisterPublisherTestBase,
  test_messages.MessageShouldProvideIMessage, support.TestCase):

    def _get_result_interfaces(self):
        from m4us import interfaces
        base_interfaces = \
          test_messages.MessageShouldProvideIMessage._get_result_interfaces(
          self)
        return base_interfaces + (interfaces.IRegisterPublisher,)


class TestRegisterPublisherShouldAcceptKeywordArguments(
  RegisterPublisherTestBase, test_messages.MessageShouldAcceptKeywordArguments,
  support.TestCase):

    pass


#---  UnregisterPublisher tests

class UnregisterPublisherTestBase(PublisherKwargsMixin,
  support.CommonTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.UnregisterPublisher


class TestUnregisterPublisherShouldProvideInterfaces(
  UnregisterPublisherTestBase, test_messages.MessageShouldProvideIMessage,
  support.TestCase):

    def _get_result_interfaces(self):
        from m4us import interfaces
        base_interfaces = \
          test_messages.MessageShouldProvideIMessage._get_result_interfaces(
          self)
        return base_interfaces + (interfaces.IUnregisterPublisher,)


class TestUnregisterPublisherShouldAcceptKeywordArguments(
  UnregisterPublisherTestBase,
  test_messages.MessageShouldAcceptKeywordArguments, support.TestCase):

    pass


#---  NotRegisteredError tests

class NotRegisteredErrorTestBase(PublisherKwargsMixin, support.CommonTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.NotRegisteredError


class TestNotRegisteredErrorShouldHaveADefaultMessage(
  NotRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestNotRegisteredErrorShouldAcceptPositionalArguments(
  NotRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestNotRegisteredErrorShouldAcceptKeywordArguments(
  NotRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestNotRegisteredErrorShouldProvideAFormattedMessage(
  NotRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  AlreadyRegisteredError tests

class AlreadyRegisteredErrorTestBase(PublisherKwargsMixin,
  support.CommonTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.AlreadyRegisteredError


class TestAlreadyRegisteredErrorShouldHaveADefaultMessage(
  AlreadyRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestAlreadyRegisteredErrorShouldAcceptPositionalArguments(
  AlreadyRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestAlreadyRegisteredErrorShouldAcceptKeywordArguments(
  AlreadyRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestAlreadyRegisteredErrorShouldProvideAFormattedMessage(
  AlreadyRegisteredErrorTestBase,
  test_exceptions.ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  Backplane Tests

class BackplaneTestBase(test_coroutines.CoroutineTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.backplane

    def _get_registerpublisher_class(self):
        from m4us import backplanes
        return backplanes.RegisterPublisher

    def _get_unregisterpublisher_class(self):
        from m4us import backplanes
        return backplanes.UnregisterPublisher

    def _make_registration_message(self, publisher=None, _message_class=None):
        if publisher is None:
            publisher = 'some publisher'
        if _message_class is None:
            _message_class = self._get_registerpublisher_class()
        return ('control', _message_class(publisher=publisher))

    def _make_unregistration_message(self, publisher=None):
        return self._make_registration_message(publisher,
          _message_class=self._get_unregisterpublisher_class())


class TestBackplaneShouldProvideICoroutine(BackplaneTestBase,
  test_coroutines.CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestBackplaneShouldAcceptAndEmitMessages(BackplaneTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestBackplaneShouldSupportThrowingExceptions(BackplaneTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestBackplaneShouldSupportBeingClosed(BackplaneTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestBackplaneShouldRespondToShutdownMessages(BackplaneTestBase,
  test_coroutines.CoroutineShouldRespondToShutdownMessages, support.TestCase):

    def test_it_should_not_emit_ishutdown_until_no_publishers(self):
        backplane = self._call_sut()
        registration_message_1 = self._make_registration_message('p1')
        unregistration_message_1 = self._make_unregistration_message('p1')
        registration_message_2 = self._make_registration_message('p2')
        unregistration_message_2 = self._make_unregistration_message('p2')
        shutdown_message = self._make_shutdown_message()
        shutdown_message = ('control', shutdown_message)
        backplane.send(registration_message_1)
        backplane.send(registration_message_2)
        for _ in xrange(5):
            result = backplane.send(shutdown_message)
            self.assert_is_none(result)
        backplane.send(unregistration_message_1)
        result = backplane.send(shutdown_message)
        self.assert_is_none(result)
        backplane.send(unregistration_message_2)
        # This is where we want the IShutdown messages to be emitted, not any
        # sooner.
        shutdown_message = self._make_shutdown_message()
        self.assert_coroutine_forwards_ishutdown_message(backplane,
          shutdown_message)

    def test_backplane_should_not_shutdown_until_no_publishers(self):
        backplane = self._call_sut()
        registration_message_1 = self._make_registration_message('p1')
        unregistration_message_1 = self._make_unregistration_message('p1')
        registration_message_2 = self._make_registration_message('p2')
        unregistration_message_2 = self._make_unregistration_message('p2')
        shutdown_message = self._make_shutdown_message()
        shutdown_message = ('control', shutdown_message)
        backplane.send(registration_message_1)
        backplane.send(registration_message_2)
        backplane.send(shutdown_message)
        backplane.send(unregistration_message_1)
        backplane.send(shutdown_message)
        backplane.send(unregistration_message_2)
        # This is where we want the StopIteration, not any sooner.
        shutdown_message = self._make_shutdown_message()
        self.assert_coroutine_shuts_down_on_message(backplane,
          shutdown_message)


class TestBackplaneShouldProvideIBackplane(BackplaneTestBase,
  support.ObjectShouldProvideInterface, support.TestCase):

    def _get_sut_interfaces(self):
        from m4us import interfaces
        return (interfaces.IBackplaneFactory,)

    def _get_result_interfaces(self):
        from m4us import interfaces
        return (interfaces.IBackplane,)


class TestBackplaneShouldSupportPublisherRegistration(BackplaneTestBase,
  support.TestCase):

    def _get_alreadyregisterederror_class(self):
        from m4us import backplanes
        return backplanes.AlreadyRegisteredError

    def test_it_should_accept_publisher_registration(self):
        backplane = self._call_sut()
        registration_message = self._make_registration_message()
        result = backplane.send(registration_message)
        self.assert_is_none(result)

    def test_it_should_raise_alreadyregisterederror_if_registered(self):
        backplane = self._call_sut()
        registration_message = self._make_registration_message()
        backplane.send(registration_message)
        already_registered_error_class = \
          self._get_alreadyregisterederror_class()
        with self.assert_raises(already_registered_error_class):
            backplane.send(registration_message)


class TestBackplaneShouldSupportPublisherUnregistration(BackplaneTestBase,
  support.TestCase):

    def _get_notregisterederror_class(self):
        from m4us import backplanes
        return backplanes.NotRegisteredError

    def test_it_should_accept_publisher_unregistration(self):
        backplane = self._call_sut()
        registration_message = self._make_registration_message()
        unregistration_message = self._make_unregistration_message()
        backplane.send(registration_message)
        result = backplane.send(unregistration_message)
        self.assert_is_none(result)

    def test_it_should_raise_notregisterederror_if_not_registered(self):
        backplane = self._call_sut()
        unregistration_message = self._make_unregistration_message()
        not_registered_error_class = self._get_notregisterederror_class()
        with self.assert_raises(not_registered_error_class):
            backplane.send(unregistration_message)


#---  Publisher tests

class PublisherTestBase(test_coroutines.CoroutineTestBase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.Publisher

    def _get_iregisterpublisher_interface(self):
        from m4us import interfaces
        return interfaces.IRegisterPublisher

    def assert_first_message_is_iregisterpublisher(self, publisher,
      message=None):
        if message is None:
            message = self._get_messages()[0]
        outbox, response = publisher.send(message)
        self.assert_equal(outbox, 'signal')
        iregisterpublisher_interface = self._get_iregisterpublisher_interface()
        self.assert_true(iregisterpublisher_interface(response, False))

    def assert_nth_post_shutdown_message_interface(self, publisher,
      message_count, shutdown_message, expected_interface):
        self.assert_first_message_is_iregisterpublisher(publisher)
        for _ in xrange(message_count):
            outbox, message = publisher.send(('control', shutdown_message))
        self.assert_equal(outbox, 'signal')
        self.assert_true(expected_interface(message, False),
          'Message {0} after IShutdown was not an {1}.'.format(message_count,
          expected_interface.getName()))


class TestPublisherShouldProvideICoroutine(PublisherTestBase,
  test_components.ComponentShouldProvideICoroutine, support.TestCase):

    pass


class TestPublisherShouldAcceptAndEmitMessages(PublisherTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    def test_it_should_accept_and_emit_messages(self):
        # Overridden
        publisher = self._call_sut()
        messages = self._get_messages()
        responses = self._get_responses()
        self.assert_first_message_is_iregisterpublisher(publisher, messages[0])
        # [(m2, r1), (m1, r2), (m2, r1)]
        for message, response in zip((messages * 2)[1:], responses * 2):
            self.assert_equal(publisher.send(message), response)


class TestPublisherShouldSupportThrowingExceptions(PublisherTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestPublisherShouldSupportBeingClosed(PublisherTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestPublisherShouldRespondToShutdownMessages(PublisherTestBase,
  test_coroutines.CoroutineShouldRespondToShutdownMessages, support.TestCase):

    def _get_iproducerfinished_interface(self):
        from m4us.core import interfaces
        return interfaces.IProducerFinished

    def test_it_should_forward_the_shutdown_message(self):
        # Overridden
        # _main should emit IShutdown as the third message after the incomming
        # IShutdown
        publisher = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        ishutdown_interface = self._get_ishutdown_interface()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          shutdown_message, ishutdown_interface)

    def test_it_should_shutdown_on_shutdown_message(self):
        # Overridden
        # _main should raise StopIteration after IShutdown is emitted.
        publisher = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        ishutdown_interface = self._get_ishutdown_interface()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          shutdown_message, ishutdown_interface)
        shutdown_message = self._make_shutdown_message()
        with self.assert_raises(StopIteration):
            publisher.send(('signal', shutdown_message))

    def test_it_should_forward_the_producerfinished_message(self):
        # Overridden
        publisher = self._call_sut()
        producer_finished_message = self._make_producer_finished_message()
        iproducerfinished_interface = self._get_iproducerfinished_interface()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          producer_finished_message, iproducerfinished_interface)

    def test_it_should_shutdown_on_producerfinished_message(self):
        # Overridden
        publisher = self._call_sut()
        producer_finished_message = self._make_producer_finished_message()
        iproducerfinished_interface = self._get_iproducerfinished_interface()
        self.assert_nth_post_shutdown_message_interface(publisher, 3,
          producer_finished_message, iproducerfinished_interface)
        shutdown_message = self._make_shutdown_message()
        with self.assert_raises(StopIteration):
            publisher.send(('signal', shutdown_message))


class TestPublisherShouldAcceptKeywordArguments(PublisherTestBase,
  test_components.ComponentShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestPublisherShouldAnInternalCoroutine(PublisherTestBase,
  test_components.ComponentShouldSupportAnInternalCoroutine, support.TestCase):

    def test_it_should_initialize_the_contained_coroutine(self):
        # Overridden
        publisher = self._call_sut()
        self.assert_true(hasattr(publisher, '_coroutine'))
        self.assert_first_message_is_iregisterpublisher(publisher)


class TestPublisherMainShouldAcceptAndEmitMessages(PublisherTestBase,
  support.TestCase):

    def test_main_should_emit_iregisterpublisher_as_first_message(self):
        publisher = self._call_sut()
        self.assert_first_message_is_iregisterpublisher(publisher)

    def test_main_should_emit_first_incomming_message_as_second_message(self):
        publisher = self._call_sut()
        messages = self._get_messages()
        expected_response = self._get_responses()[0]
        self.assert_first_message_is_iregisterpublisher(publisher, messages[0])
        response = publisher.send(messages[1])
        self.assert_equal(response, expected_response)

    def test_main_should_ignore_none_messages_on_control_inbox(self):
        publisher = self._call_sut()
        message = self._get_messages()[0]
        publisher.send(('control', None))
        result = publisher.send(message)
        self.assert_is_none(result)


class TestPublisherMainShouldRespondToShutdownMessages(PublisherTestBase,
  ShutdownMessageMixin, support.TestCase):

    def _get_iunregisterpublisher_interface(self):
        from m4us import interfaces
        return interfaces.IUnregisterPublisher

    def test_main_should_emit_previous_message_first_on_ishutdown(self):
        publisher = self._call_sut()
        message = self._get_messages()[0]
        expected_response = self._get_responses()[0]
        shutdown_message = self._make_shutdown_message()
        shutdown_message = ('control', shutdown_message)
        self.assert_first_message_is_iregisterpublisher(publisher, message)
        response = publisher.send(shutdown_message)
        self.assert_equal(response, expected_response)

    def test_main_should_emit_iunregisterpublisher_second_on_ishutdown(self):
        publisher = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        iunregisterpublisher_interface = \
          self._get_iunregisterpublisher_interface()
        self.assert_nth_post_shutdown_message_interface(publisher, 2,
          shutdown_message, iunregisterpublisher_interface)


class TestPublishTo(ShutdownMessageMixin, support.CommonTestBase,
  support.TestCase):

    def _get_sut(self):
        from m4us import backplanes
        return backplanes.publish_to

    def _get_required_args(self):
        return (mock.Mock(),)

    def _get_icontainer_interface(self):
        from m4us.core import interfaces
        return interfaces.IContainer

    def test_it_should_raise_typeerror_if_no_argument_given(self):
        with self.assert_raises(TypeError):
            ## pylint: disable=E1120
            self._get_sut()()
            ## pylint: enable=E1120

    def test_it_should_return_an_icontainer(self):
        publishing_coroutine = self._call_sut()
        icontainer_interface = self._get_icontainer_interface()
        self.assert_true(icontainer_interface(publishing_coroutine, False))

    def test_it_should_not_emit_normal_messages(self):
        publishing_coroutine = self._call_sut()
        message = ('inbox', 'some message')
        result = publishing_coroutine.coroutines[-1].send(message)
        self.assert_is_none(result)

    def test_it_should_forward_ishutdown_messages(self):
        publishing_coroutine = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        shutdown_message = ('control', shutdown_message)
        result = publishing_coroutine.coroutines[-1].send(shutdown_message)
        self.assert_is_not_none(result)
        ishutdown_interface = self._get_ishutdown_interface()
        self.assert_true(ishutdown_interface(result[1], False))


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
