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


"""Tests for m4us.core.coroutines."""

## pylint:disable=C0302


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import inspect
import types

#---  Third-party imports
import unittest2
import mock
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def plain_coroutine():
    message = (yield)
    while True:
        try:
            message = (yield message)
        ## pylint: disable=W0703
        except Exception as error:
            ## pylint: enable=W0703
            message = ('exception', error)


def make_decorated_coroutine():
    from m4us.core import coroutines

    @coroutines.coroutine()
    def decorated_coroutine():
        return plain_coroutine()

    return decorated_coroutine


def make_non_lazy_coroutine():
    from m4us.core import coroutines

    @coroutines.coroutine(lazy=False)
    def non_lazy_coroutine():
        return plain_coroutine()

    return non_lazy_coroutine


def make_coroutine_with_parameters():
    from m4us.core import coroutines

    @coroutines.coroutine()
    def coroutine_with_parameters(first, second, third=None, fourth=None):
        yield
        yield 'outbox', dict(first=first, second=second, third=third,
          fourth=fourth)

    return coroutine_with_parameters


def make_coroutine_with_custom_interfaces():
    from m4us.core import coroutines

    @coroutines.coroutine()
    @interface.implementer(support.IDummy)
    @interface.provider(support.IDummyFactory)
    def coroutine_with_custom_interfaces():
        return plain_coroutine()

    return coroutine_with_custom_interfaces


def filter_function(message, required, optional=1, *args, **kwargs):
    """Test filter for the filter_ decorator."""
    return '{0} {1} {2} {3} {4}'.format(message, required, optional,
      repr(args), repr(kwargs))


def producer_function(required, optional=True, *args, **kwargs):
    """Test generator for the producer decorator."""
    for _ in range(5):
        yield '{0} {1} {2} {3} {4}'.format(required, optional, repr(args),
          repr(kwargs))


#---Classes--------------------------------------------------------------------

class DummyIterable(object):

    def __iter__(self):
        return self

    def next(self):
        return 0


class CoroutineTestBase(support.CommonTestBase):

    def _get_messages(self):
        message1 = ('inbox', 'Hello')
        message2 = ('inbox', 'Message 2')
        return (message1, message2)

    def _get_responses(self):
        response1 = ('outbox', 'Hello')
        response2 = ('outbox', 'Message 2')
        return (response1, response2)

    def _get_exception(self):
        return support.DummyException

    def _get_inotlazy_interface(self):
        from m4us.core import interfaces
        return interfaces.INotLazy

    def assert_throw_yields_message(self, coroutine, exception, message):
        result = coroutine.throw(exception)
        self.assert_equal(result, message)

    def assert_is_lazy(self, coroutine):
        inotlazy_interface = self._get_inotlazy_interface()
        self.assert_false(inotlazy_interface.providedBy(coroutine))
        self.assert_false(inotlazy_interface(coroutine, False))

    def assert_not_lazy(self, coroutine):
        inotlazy_interface = self._get_inotlazy_interface()
        self.assert_true(inotlazy_interface(coroutine, False))

    def assert_adapts_to_inotlazy(self, coroutine):
        inotlazy_interface = self._get_inotlazy_interface()
        self.assert_false(inotlazy_interface.providedBy(coroutine))
        self.assert_not_lazy(coroutine)


class BasicMessagesMixin(object):

    def _get_messages(self):
        return ('Hello', 'Message 2')

    def _get_responses(self):
        return self._get_messages()


class CoroutineShouldProvideICoroutine(support.ObjectShouldProvideInterface):

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.ICoroutineFactory,)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.ICoroutine,)


class CoroutineShouldProvideINotLazy(support.ObjectShouldProvideInterface):

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.INotLazy,)

    test_it_should_provide_required_interfaces = None


class CoroutineShouldAcceptAndEmitMessages(CoroutineTestBase):

    def test_it_should_accept_and_emit_messages(self):
        coroutine = self._call_sut()
        messages = self._get_messages()
        responses = self._get_responses()
        for message, response in zip(messages, responses):
            self.assert_equal(coroutine.send(message), response)

    def test_it_should_not_raise_typeerror_if_first_message_not_none(self):
        coroutine = self._call_sut()
        message = self._get_messages()[0]
        with self.assert_not_raises(TypeError):
            coroutine.send(message)


class CoroutineShouldSupportThrowingExceptions(CoroutineTestBase):

    def test_throw_should_raise_unhandled_thrown_exception(self):
        coroutine = self._call_sut()
        exception = self._get_exception()
        with self.assert_raises(exception):
            coroutine.throw(exception())


class CoroutineShouldSupportDelayedExceptions(CoroutineTestBase):

    def test_throw_should_return_yielded_results(self):
        coroutine = self._call_sut()
        primer_message = self._get_messages()[0]
        exception = self._get_exception()()
        message = ('exception', exception)
        coroutine.send(primer_message)  # Put the coroutine in the while loop.
        self.assert_throw_yields_message(coroutine, exception, message)


class CoroutineShouldSupportBeingClosed(CoroutineTestBase):

    def test_send_should_raise_stopiteration_if_coroutine_is_closed(self):
        coroutine = self._call_sut()
        coroutine.close()
        with self.assert_raises(StopIteration):
            coroutine.send('This should fail')

    def test_throw_should_raise_given_exception_if_coroutine_is_closed(self):
        coroutine = self._call_sut()
        coroutine.close()
        with self.assert_raises(support.DummyException):
            coroutine.throw(support.DummyException())

    def test_repeated_calls_to_close_should_have_no_effect(self):
        coroutine = self._call_sut()
        coroutine.close()
        with self.assert_not_raises(Exception):
            for _ in xrange(5):
                coroutine.close()


class CoroutineShouldRespondToShutdownMessages(CoroutineTestBase):

    def _get_ishutdown_interface(self):
        from m4us.core import interfaces
        return interfaces.IShutdown

    def _make_shutdown_message(self):
        from m4us.core import messages
        return messages.Shutdown()

    def _make_producer_finished_message(self):
        from m4us.core import messages
        return messages.ProducerFinished()

    def assert_coroutine_shuts_down_on_message(self, coroutine, message):
        coroutine.send(('control', message))
        with self.assert_raises(StopIteration):
            coroutine.send('This should fail')

    def assert_coroutine_forwards_ishutdown_message(self, coroutine, message):
        ishutdown_interface = self._get_ishutdown_interface()
        outbox, message = coroutine.send(('control', message))
        self.assert_equal(outbox, 'signal')
        self.assert_true(ishutdown_interface(message, False))

    #---  IShutdown tests

    def test_it_should_shutdown_on_shutdown_message(self):
        coroutine = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        self.assert_coroutine_shuts_down_on_message(coroutine,
          shutdown_message)

    def test_it_should_forward_the_shutdown_message(self):
        coroutine = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        self.assert_coroutine_forwards_ishutdown_message(coroutine,
          shutdown_message)

    #---  IProducerFinished tests

    def test_it_should_shutdown_on_producerfinished_message(self):
        coroutine = self._call_sut()
        producer_finished_message = self._make_producer_finished_message()
        self.assert_coroutine_shuts_down_on_message(coroutine,
          producer_finished_message)

    def test_it_should_forward_the_producerfinished_message(self):
        coroutine = self._call_sut()
        producer_finished_message = self._make_producer_finished_message()
        self.assert_coroutine_forwards_ishutdown_message(coroutine,
          producer_finished_message)


#---  _Interface_adapter_hook tests

class TestCoroutineInterfaceAdapterHook(support.CommonTestBase,
  support.TestCase):

    #---  Support methods

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines._interface_adapter_hook

    def _get_interface(self):
        return support.IDummy

    def _make_mock_coroutine(self):
        return mock.Mock(name='coroutine', spec_set=[])

    def _make_mock_stand_in_registry(self):
        from m4us.core import utils
        return mock.MagicMock(spec_set=utils._ObjectStandInRegistry)

    def _get_global_registry_name(self):
        return b'm4us.core.coroutines._coroutine_stand_in_registry'

    #---  Tests

    def test_it_should_accept_an_interface_and_a_coroutine(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        with self.assert_not_raises(TypeError):
            self._call_sut(some_interface, coroutine)

    def test_it_should_accept_an_optional_registry_argument(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        registry = self._make_mock_stand_in_registry()
        with self.assert_not_raises(TypeError):
            self._call_sut(some_interface, coroutine, registry)

    def test_it_should_return_coroutine_if_stand_in_provides_interface(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        registry = self._make_mock_stand_in_registry()
        stand_in = registry[coroutine]
        interface.directlyProvides(stand_in, some_interface)
        result = self._call_sut(some_interface, coroutine, registry)
        self.assert_is(result, coroutine)

    def test_it_should_return_none_if_stand_in_not_provide_interface(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        registry = self._make_mock_stand_in_registry()
        result = self._call_sut(some_interface, coroutine, registry)
        self.assert_is(result, None)

    def test_it_should_use_global_registry_if_registry_not_given(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        registry = self._make_mock_stand_in_registry()
        global_registry_name = self._get_global_registry_name()
        with mock.patch(global_registry_name, registry):
            self._call_sut(some_interface, coroutine)
            self.assert_true(registry.__getitem__.called)

    def test_it_should_be_called_by_zope_interface_during_adaptation(self):
        some_interface = self._get_interface()
        coroutine = self._make_mock_coroutine()
        registry = self._make_mock_stand_in_registry()
        global_registry_name = self._get_global_registry_name()
        with mock.patch(global_registry_name, registry):
            interface.directlyProvides(registry[coroutine], some_interface)
            result = some_interface(coroutine, 'Not adapted!')
        self.assert_is(result, coroutine)

    def test_it_should_not_raise_typeerror_on_invalid_coroutine_types(self):
        some_interface = self._get_interface()
        registry = self._make_mock_stand_in_registry()
        registry.__getitem__.side_effect = TypeError
        with self.assert_not_raises(TypeError):
            self._call_sut(some_interface, ['something invalid'], registry)


#---  Raw coroutine tests

class RawCoroutineTestBase(support.CommonTestBase):

    def _get_sut(self):
        return plain_coroutine


class TestRawCoroutineShouldProvideICoroutine(RawCoroutineTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    test_it_should_provide_required_interfaces = None


class TestRawCoroutineShouldRequireNoneAsFirstMessage(RawCoroutineTestBase,
  support.TestCase):

    def test_it_should_raise_typeerror_if_first_message_is_not_none(self):
        coroutine = self._call_sut()
        with self.assert_raises(TypeError):
            coroutine.send('Hello')


#---  Basic coroutine tests

class BasicCoroutineTestBase(BasicMessagesMixin, CoroutineTestBase):

    def _get_sut(self):
        return make_decorated_coroutine()


class TestBasicCoroutineShouldProvideICoroutine(BasicCoroutineTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestBasicCoroutineShouldAcceptAndEmitMessages(BasicCoroutineTestBase,
  CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestBasicCoroutineShouldSupportThrowingExceptions(BasicCoroutineTestBase,
  CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestBasicCoroutineShouldSupportDelayedExceptions(BasicCoroutineTestBase,
  CoroutineShouldSupportDelayedExceptions, support.TestCase):

    pass


class TestBasicCoroutineShouldSupportBeingClosed(BasicCoroutineTestBase,
  CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


#---  Sample coroutine tests

class SampleCoroutineTestBase(CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.sample_coroutine


class TestSampleCoroutineShouldProvideICoroutine(SampleCoroutineTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestSampleCoroutineShouldAcceptAndEmitMessages(SampleCoroutineTestBase,
  CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestSampleCoroutineShouldSupportThrowingExceptions(
  SampleCoroutineTestBase, CoroutineShouldSupportThrowingExceptions,
  support.TestCase):

    pass


class TestSampleCoroutineShouldSupportBeingClosed(SampleCoroutineTestBase,
  CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestSampleCoroutineShouldRespondToShutdownMessages(
  SampleCoroutineTestBase, CoroutineShouldRespondToShutdownMessages,
  support.TestCase):

    pass


#---  Coroutine decorator tests

class TestCoroutineDecoratorShouldMakeCoroutines(BasicMessagesMixin,
  support.CommonTestBase, support.TestCase):

    def _get_sut(self):
        return make_coroutine_with_parameters()

    def _get_required_args(self):
        return (1, 2)

    def test_it_should_initialize_the_coroutine_when_called(self):
        coroutine = self._call_sut()
        with self.assert_not_raises(TypeError):
            coroutine.send('Non-None value')

    def test_it_should_pass_all_args_to_the_decorated_function(self):
        coroutine = self._call_sut(9, 8, fourth=7, third=6)
        message = self._get_messages()[0]
        _, kwargs = coroutine.send(message)
        self.assert_equal(dict(first=9, second=8, third=6, fourth=7), kwargs)


class TestCoroutineDecoratorShouldSupportCoroutineLazyness(CoroutineTestBase,
  support.TestCase):

    def _get_sut(self):
        return make_decorated_coroutine()

    def make_non_lazy_coroutine(self):
        return make_non_lazy_coroutine()()

    def test_it_should_support_setting_coroutine_laziness(self):
        lazy_coroutine = self._call_sut()
        non_lazy_coroutine_ = self.make_non_lazy_coroutine()
        self.assert_is_lazy(lazy_coroutine)
        self.assert_not_lazy(non_lazy_coroutine_)


class TestCoroutineDecoratorShouldPreserveInterfaces(support.CommonTestBase,
  support.TestCase):

    def _get_sut(self):
        return make_coroutine_with_custom_interfaces()

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.ICoroutineFactory, support.IDummyFactory)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.ICoroutine, support.IDummy)

    def test_it_should_preserve_factory_provided_interfaces(self):
        factory = self._get_sut()
        factory_interfaces = self._get_sut_interfaces()
        self.assert_interfaces(factory, factory_interfaces)

    def test_it_should_make_coroutine_provide_implemented_interfaces(self):
        coroutine = self._call_sut()
        coroutine_interfaces = self._get_result_interfaces()
        self.assert_interfaces(coroutine, coroutine_interfaces)


#---  Null_sink tests

class NullSinkTestBase(CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.null_sink


class TestNullSinkShouldProvideICoroutine(NullSinkTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestNullSinkShouldAcceptAndEmitMessages(NullSinkTestBase,
  CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    # Overridden and removed because it does not apply.
    test_it_should_accept_and_emit_messages = None

    def test_it_should_accept_but_not_emit_non_shutdown_messages(self):
        coroutine = self._call_sut()
        message = self._get_messages()[0]
        response = coroutine.send(message)
        self.assert_is(response, None)


class TestNullSinkShouldSupportThrowingExceptions(NullSinkTestBase,
  CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestNullSinkShouldSupportBeingClosed(NullSinkTestBase,
  CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestNullSinkShouldRespondToShutdownMessages(
  NullSinkTestBase, CoroutineShouldRespondToShutdownMessages,
  support.TestCase):

    pass


#---  filter_from_callable tests

class FilterFromCallableTestBase(CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.filter_from_callable

    def _get_required_args(self):
        # Default callable just returns whatever message it is given.
        return (lambda message: message,)


class TestFilterFromCallableShouldProvideICoroutine(FilterFromCallableTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestFilterFromCallableShouldAcceptAndEmitMessages(
  FilterFromCallableTestBase, CoroutineShouldAcceptAndEmitMessages,
  support.TestCase):

    pass


class TestFilterFromCallableShouldSupportThrowingExceptions(
  FilterFromCallableTestBase, CoroutineShouldSupportThrowingExceptions,
  support.TestCase):

    pass


class TestFilterFromCallableShouldSupportBeingClosed(
  FilterFromCallableTestBase, CoroutineShouldSupportBeingClosed,
  support.TestCase):

    pass


class TestFilterFromCallableShouldRespondToShutdownMessages(
  FilterFromCallableTestBase, CoroutineShouldRespondToShutdownMessages,
  support.TestCase):

    def test_it_should_emit_ishutdowns_returned_from_callable(self):
        message = self._get_messages()[0]
        shutdown_message = self._make_shutdown_message()
        ishutdown_interface = self._get_ishutdown_interface()
        callable_ = mock.Mock(return_value=shutdown_message)
        filter_ = self._call_sut(callable_)
        result = filter_.send(message)
        self.assert_equal(result[0], 'signal')
        self.assert_true(ishutdown_interface(result[1], False))
        self.assert_is(result[1], shutdown_message)

    def test_it_should_shutdown_when_ishutdown_returned_from_callable(self):
        messages = self._get_messages()
        shutdown_message = self._make_shutdown_message()
        callable_ = mock.Mock(return_value=shutdown_message)
        filter_ = self._call_sut(callable_)
        filter_.send(messages[0])
        with self.assert_raises(StopIteration):
            filter_.send(messages[1])


class TestFilterFromCallableShouldAcceptArguments(FilterFromCallableTestBase,
  support.TestCase):

    def test_it_should_accept_a_positional_argument(self):
        argument = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(argument)

    def test_it_should_require_an_argument(self):
        with self.assert_raises(TypeError):
            ## pylint: disable=E1120
            self._get_sut()()
            ## pylint: enable=E1120

    def test_it_should_require_a_callable_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut('Not a callable')

    def test_it_should_accept_additional_arguments(self):
        argument = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(argument, 'other', 'positional', 'arguments',
              additional='keyword', arguments='accepted')


class TestFilterFromCallableShouldPassMessagesThroughCallable(
  FilterFromCallableTestBase, support.TestCase):

    def test_it_should_call_callable_with_each_inbox_message(self):
        callable_ = mock.Mock()
        filter_ = self._call_sut(callable_)
        messages = self._get_messages()
        for message in messages:
            filter_.send(message)
            callable_.assert_called_with(message[1])
        self.assert_equal(callable_.call_count, 2)

    def test_it_should_pass_all_additional_arguments_to_the_callable(self):
        callable_ = mock.Mock()
        filter_ = self._call_sut(callable_, 'a', 'b', c='3', d='4')
        messages = self._get_messages()
        for message in messages:
            filter_.send(message)
            callable_.assert_called_with(message[1], 'a', 'b', c='3', d='4')
        self.assert_equal(callable_.call_count, 2)

    def test_it_should_emit_results_from_callable_on_outbox(self):
        # By sending in lower-case messages and expecting upper-case in
        # response, this test ensure that messages are not just blindly being
        # passed through like in sample_coroutine.
        messages = self._get_messages()
        messages = [(inbox, message.lower()) for inbox, message in messages]
        expected_responses = self._get_responses()
        expected_responses = [(outbox, message.upper()) for outbox, message in
          expected_responses]
        callable_results = [response[1] for response in expected_responses]
        callable_ = lambda message: callable_results.pop(0)
        filter_ = self._call_sut(callable_)
        for message, expected_response in zip(messages, expected_responses):
            response = filter_.send(message)
            self.assert_equal(response, expected_response)

    def test_it_should_ignore_all_non_inbox_messages_except_ishutdown(self):
        messages = self._get_messages()
        control_messages = [('control', message[1]) for message in messages]
        non_inbox_messages = [('notabox', message[1]) for message in messages]
        callable_ = mock.Mock(return_value='some result')
        filter_ = self._call_sut(callable_)
        for message in control_messages + non_inbox_messages:
            response = filter_.send(message)
            self.assert_is(response, None)
        self.assert_false(callable_.called)


class TestFilterFromCallableShouldSuppressNonesWhenAsked(
  FilterFromCallableTestBase, support.TestCase):

    def _get_required_args(self):
        return (lambda message: None,)

    def test_it_should_accept_suppress_none_as_kwarg(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(suppress_none=True)

    def test_it_should_not_pass_suppress_none_to_function(self):
        message = self._get_messages()[0]
        mock_function = mock.Mock()
        filter_ = self._call_sut(mock_function, suppress_none=True)
        filter_.send(message)
        self.assert_not_in('suppress_none', mock_function.call_args[1])
        mock_function.assert_called_once_with(message[1])

    def test_it_should_emit_none_on_outbox_if_suppress_none_is_false(self):
        message = self._get_messages()[0]
        filter_ = self._call_sut(suppress_none=False)
        result = filter_.send(message)
        self.assert_tuple_equal(result, ('outbox', None))

    def test_it_should_emit_none_on_outbox_if_suppress_none_not_given(self):
        message = self._get_messages()[0]
        filter_ = self._call_sut()
        result = filter_.send(message)
        self.assert_tuple_equal(result, ('outbox', None))

    def test_it_should_not_emit_none_on_outbox_if_suppress_none_is_true(self):
        message = self._get_messages()[0]
        filter_ = self._call_sut(suppress_none=True)
        result = filter_.send(message)
        self.assert_is_none(result)


#---  filter_ decorator tests

class FilterTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.filter_

    def _get_required_args(self):
        return (lambda message: message,)


class TestFilterShouldBeADecorator(FilterTestBase, support.TestCase):

    def test_it_should_accept_a_function_as_a_positional_argument(self):
        function = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(function)

    def test_it_should_require_a_function_as_a_positional_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut('Not a function')

    def test_it_should_require_a_function_with_at_least_one_parameter(self):
        with self.assert_raises(ValueError):
            self._call_sut(lambda: 'outbox message')

    def test_it_should_accept_a_function_with_star_args(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(lambda *args: args)

    def test_it_should_return_a_callable(self):
        result = self._call_sut()
        self.assert_true(callable(result))


class TestFilterShouldCreateACoroutine(FilterTestBase, support.TestCase):

    def _get_icoroutinefactory_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutineFactory

    def test_it_should_return_an_icoroutine_factory(self):
        icoroutinefactory_interface = self._get_icoroutinefactory_interface()
        filter_factory = self._call_sut()
        self.assert_interfaces(filter_factory, [icoroutinefactory_interface])

    def test_filter_factory_should_call_filter_from_callable(self):
        function = self._get_required_args()[0]
        filter_factory = self._call_sut(function)
        with mock.patch('m4us.core.coroutines.filter_from_callable') as \
          mock_filter_from_callable:
            filter_factory()
        mock_filter_from_callable.assert_called_once_with(function)

    def test_filter_factory_should_return_filter_from_callable_result(self):
        expected_result = 'filter_from_callable return value'
        filter_factory = self._call_sut()
        with mock.patch('m4us.core.coroutines.filter_from_callable') as \
          mock_filter_from_callable:
            mock_filter_from_callable.return_value = expected_result
            filter_coroutine = filter_factory()
        self.assert_is(filter_coroutine, expected_result)


class TestFilterShouldHaveCorrectSignatureAndDocstring(FilterTestBase,
  support.TestCase):

    def _get_required_args(self):
        return (filter_function,)

    def test_it_should_preserve_docstring(self):
        function = self._get_required_args()[0]
        filter_factory = self._call_sut()
        self.assert_equal(filter_factory.__doc__, function.__doc__)

    def test_it_should_call_strip_first_parameter(self):
        with mock.patch('m4us.core.utils._strip_first_parameter') as \
          mock_strip_first_parameter:
            self._call_sut()
        self.assert_true(mock_strip_first_parameter.called)

    def test_filter_factory_should_actualy_require_required_arguments(self):
        filter_factory = self._call_sut()
        with self.assert_raises(TypeError):
            filter_factory()
        with self.assert_not_raises(TypeError):
            filter_factory('required value')


#---  producer_from_iterable tests

class ProducerFromIterableTestBase(CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.producer_from_iterable

    def _get_required_args(self):
        # Default iterable just counts to 0 to 4.
        return (xrange(5),)

    def _get_messages(self):
        return [('control', None)] * 5

    def _get_responses(self):
        iterable = self._get_required_args()[0]
        return [('outbox', element) for element in iterable]


class TestProducerFromIterableShouldProvideICoroutine(
  ProducerFromIterableTestBase, CoroutineShouldProvideICoroutine,
  support.TestCase):

    pass


class TestProducerFromIterableShouldAcceptAndEmitMessages(
  ProducerFromIterableTestBase, CoroutineShouldAcceptAndEmitMessages,
  support.TestCase):

    def _get_iproducerfinished_interface(self):
        from m4us.core import interfaces
        return interfaces.IProducerFinished

    def test_it_should_call_next_on_iterator_for_each_element(self):
        messages = self._get_messages()
        with mock.patch.object(DummyIterable, 'next') as mock_next:
            iterable = DummyIterable()
            producer = self._call_sut(iterable)
            for message in messages:
                producer.send(message)
        self.assert_equal(mock_next.call_count, len(messages))

    def test_it_should_emit_producerfinished_when_iterator_is_exhausted(self):
        producer = self._call_sut()
        messages = self._get_messages()
        iproducerfinished_interface = self._get_iproducerfinished_interface()
        for message in messages:
            producer.send(message)
        with self.assert_not_raises(StopIteration):
            outbox, message = producer.send(messages[0])
        self.assert_equal(outbox, 'signal')
        self.assert_interfaces(message, [iproducerfinished_interface])


class TestProducerFromIterableShouldSupportThrowingExceptions(
  ProducerFromIterableTestBase, CoroutineShouldSupportThrowingExceptions,
  support.TestCase):

    pass


class TestProducerFromIterableShouldSupportBeingClosed(
  ProducerFromIterableTestBase, CoroutineShouldSupportBeingClosed,
  support.TestCase):

    pass


class TestProducerFromIterableShouldRespondToShutdownMessages(
  ProducerFromIterableTestBase, CoroutineShouldRespondToShutdownMessages,
  support.TestCase):

    pass


class TestProducerFromIterableShouldAcceptArguments(
  ProducerFromIterableTestBase, support.TestCase):

    def test_it_should_accept_a_positional_argument(self):
        argument = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(argument)

    def test_it_should_require_an_argument(self):
        with self.assert_raises(TypeError):
            ## pylint: disable=E1120
            self._get_sut()()
            ## pylint: enable=E1120

    def test_it_should_require_an_iterable_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut(42)


#---  producer decorator tests

class ProducerTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.producer

    def _get_required_args(self):
        return (lambda: (x for x in xrange(5)),)


class TestProducerShouldBeADecorator(ProducerTestBase, support.TestCase):

    def test_it_should_accept_a_callable_as_a_positional_argument(self):
        callable_ = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(callable_)

    def test_it_should_require_a_callable_as_a_positional_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut('Not a callable')

    def test_it_should_return_a_callable(self):
        result = self._call_sut()
        self.assert_true(callable(result))


class TestProducerShouldPreserveSignatureAndDocstring(ProducerTestBase,
  support.TestCase):

    def _get_required_args(self):
        return (producer_function,)

    def test_it_should_preserve_the_docstring(self):
        result = self._call_sut()
        self.assert_equal(result.__doc__, producer_function.__doc__)

    def test_it_should_preserve_the_signature(self):
        expected_signature = inspect.getargspec(producer_function)
        result = self._call_sut()
        result_signature = inspect.getargspec(result)
        self.assert_tuple_equal(expected_signature, result_signature)


class TestProducerShouldCreateACoroutine(ProducerTestBase, support.TestCase):

    def _get_icoroutinefactory_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutineFactory

    def test_it_should_return_an_icoroutine_factory(self):
        icoroutinefactory_interface = self._get_icoroutinefactory_interface()
        producer_factory = self._call_sut()
        self.assert_interfaces(producer_factory, [icoroutinefactory_interface])

    def test_producer_factory_should_call_producer_from_iterable(self):
        producer_factory = self._call_sut()
        with mock.patch('m4us.core.coroutines.producer_from_iterable') as \
          mock_producer_from_iterable:
            producer_factory()
        self.assert_true(mock_producer_from_iterable.called)

    def test_producer_factory_should_return_producer_from_iterable_result(
      self):
        expected_result = 'producer_from_iterable return value'
        producer_factory = self._call_sut()
        with mock.patch('m4us.core.coroutines.producer_from_iterable') as \
          mock_producer_from_iterable:
            mock_producer_from_iterable.return_value = expected_result
            producer_coroutine = producer_factory()
        self.assert_is(producer_coroutine, expected_result)


#---  sink_from_callable tests

class SinkFromCallableTestBase(CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.sink_from_callable

    def _get_required_args(self):
        return (lambda message: message,)

    def _get_responses(self):
        return [None for _ in self._get_messages()]


class TestSinkFromCallableShouldProvideICoroutine(SinkFromCallableTestBase,
  CoroutineShouldProvideICoroutine, support.TestCase):

    pass


class TestSinkFromCallableShouldAcceptAndEmitMessages(
  SinkFromCallableTestBase, CoroutineShouldAcceptAndEmitMessages,
  support.TestCase):

    pass


class TestSinkFromCallableShouldSupportThrowingExceptions(
  SinkFromCallableTestBase, CoroutineShouldSupportThrowingExceptions,
  support.TestCase):

    pass


class TestSinkFromCallableShouldSupportBeingClosed(
  SinkFromCallableTestBase, CoroutineShouldSupportBeingClosed,
  support.TestCase):

    pass


class TestSinkFromCallableShouldRespondToShutdownMessages(
  SinkFromCallableTestBase, CoroutineShouldRespondToShutdownMessages,
  support.TestCase):

    def test_it_should_emit_ishutdowns_returned_from_callable(self):
        message = self._get_messages()[0]
        shutdown_message = self._make_shutdown_message()
        ishutdown_interface = self._get_ishutdown_interface()
        callable_ = mock.Mock(return_value=shutdown_message)
        sink = self._call_sut(callable_)
        result = sink.send(message)
        self.assert_is_not_none(result)
        self.assert_equal(result[0], 'signal')
        self.assert_true(ishutdown_interface(result[1], False))
        self.assert_is(result[1], shutdown_message)


class TestSinkFromCallableShouldAcceptArguments(SinkFromCallableTestBase,
  support.TestCase):

    def test_it_should_accept_a_positional_argument(self):
        argument = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(argument)

    def test_it_should_require_an_argument(self):
        with self.assert_raises(TypeError):
            ## pylint: disable=E1120
            self._get_sut()()
            ## pylint: enable=E1120

    def test_it_should_require_a_callable_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut('Not a callable')

    def test_it_should_accept_additional_arguments(self):
        argument = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(argument, 'other', 'positional', 'arguments',
              additional='keyword', arguments='accepted')


class TestSinkFromCallableShouldPassMessagesThroughCallable(
  SinkFromCallableTestBase, support.TestCase):

    def test_it_should_call_callable_with_each_inbox_message(self):
        callable_ = mock.Mock()
        sink = self._call_sut(callable_)
        messages = self._get_messages()
        for message in messages:
            sink.send(message)
            callable_.assert_called_with(message[1])
        self.assert_equal(callable_.call_count, 2)

    def test_it_should_pass_all_additional_arguments_to_the_callable(self):
        callable_ = mock.Mock()
        sink = self._call_sut(callable_, 'a', 'b', c='3', d='4')
        messages = self._get_messages()
        for message in messages:
            sink.send(message)
            callable_.assert_called_with(message[1], 'a', 'b', c='3', d='4')
        self.assert_equal(callable_.call_count, 2)

    def test_it_should_ignore_all_non_inbox_messages_except_ishutdown(self):
        messages = self._get_messages()
        control_messages = [('control', message[1]) for message in messages]
        non_inbox_messages = [('notabox', message[1]) for message in messages]
        callable_ = mock.Mock(return_value='some result')
        sink = self._call_sut(callable_)
        for message in control_messages + non_inbox_messages:
            response = sink.send(message)
            self.assert_is(response, None)
        self.assert_false(callable_.called)


#---  _curried_coroutine_factory tests

class CurriedCoroutineFactoryTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines._curried_coroutine_factory

    def _get_required_args(self):
        return (lambda message: message,
          'm4us.core.coroutines.filter_from_callable')


class TestCurriedCoroutineFactoryShouldValidateInputs(
  CurriedCoroutineFactoryTestBase, support.TestCase):

    def test_it_should_accept_a_function_as_first_argument(self):
        args = self._get_required_args()
        with self.assert_not_raises(TypeError):
            self._call_sut(lambda message: message, *args[1:])

    def test_it_should_require_a_function_as_first_argument(self):
        args = self._get_required_args()
        with self.assert_raises(TypeError):
            self._call_sut('not a function', *args[1:])

    def test_it_should_accept_a_coroutine_factory_path_as_second_argument(
      self):
        args = self._get_required_args()
        with self.assert_not_raises(TypeError):
            self._call_sut(args[0], 'm4us.core.coroutines.make_filter')

    def test_it_should_require_a_coroutine_factory_path_as_second_argument(
      self):
        args = self._get_required_args()
        with self.assert_raises(TypeError):
            self._call_sut(args[0])


class TestCurriedCoroutineFactoryShouldCreateACoroutineFactory(
  CurriedCoroutineFactoryTestBase, support.TestCase):

    def _get_coroutine_factory_template(self):
        from m4us.core import coroutines
        return coroutines._COROUTINE_FACTORY_TEMPLATE

    def _get_icoroutinefactory_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutineFactory

    def _get_icoroutine_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutine

    def test_it_should_pass_coroutine_factory_path_to_template(self):
        factory_path = self._get_required_args()[1]
        module_path, factory_name = factory_path.rsplit('.', 1)
        template = self._get_coroutine_factory_template()
        template = template.format(module_path=module_path,
          factory_name=factory_name)
        with mock.patch('m4us.core.coroutines._COROUTINE_FACTORY_TEMPLATE') as\
          mock_coroutine_factory_template:
            mock_coroutine_factory_template.format.return_value = template
            self._call_sut()
        mock_coroutine_factory_template.format.assert_called_once_with(
          module_path=module_path, factory_name=factory_name)

    def test_it_should_call_function_wrapper_from_template(self):
        function, factory_path = self._get_required_args()
        module_path, factory_name = factory_path.rsplit('.', 1)
        template = self._get_coroutine_factory_template()
        template = template.format(module_path=module_path,
          factory_name=factory_name)
        ## pylint: disable=C0103
        with mock.patch('m4us.core.utils._function_wrapper_from_template') as \
          mock_function_wrapper_from_template:
            self._call_sut(function, factory_path)
        ## pylint: enable=C0103
        mock_function_wrapper_from_template.assert_called_once_with(function,
          template, strip_first_parameter=True)

    def test_it_should_return_the_curried_factory_function(self):
        function, factory_path = self._get_required_args()
        curried_factory = self._call_sut(function, factory_path)
        self.assert_is_instance(curried_factory, types.FunctionType)
        self.assert_true(hasattr(curried_factory, 'undecorated'))
        self.assert_is(curried_factory.undecorated, function)

    def test_it_should_register_curried_factory_as_icoroutinefactory(self):
        icoroutinefactory_interface = self._get_icoroutinefactory_interface()
        curried_factory = self._call_sut()
        self.assert_interfaces(curried_factory, [icoroutinefactory_interface])

    def test_it_curried_factory_should_return_a_coroutine(self):
        icoroutine_interface = self._get_icoroutine_interface()
        curried_factory = self._call_sut()
        coroutine = curried_factory()
        self.assert_interfaces(coroutine, [icoroutine_interface])


#---  sink_ decorator tests

class SinkTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import coroutines
        return coroutines.sink

    def _get_required_args(self):
        return (lambda message: None,)


class TestSinkShouldBeADecorator(SinkTestBase, support.TestCase):

    def test_it_should_accept_a_function_as_a_positional_argument(self):
        function = self._get_required_args()[0]
        with self.assert_not_raises(TypeError):
            self._call_sut(function)

    def test_it_should_require_a_function_as_a_positional_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut('Not a function')

    def test_it_should_require_a_function_with_at_least_one_parameter(self):
        with self.assert_raises(ValueError):
            self._call_sut(lambda: None)

    def test_it_should_accept_a_function_with_star_args(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(lambda *args: None)

    def test_it_should_return_a_callable(self):
        result = self._call_sut()
        self.assert_true(callable(result))


class TestSinkShouldCreateACoroutine(SinkTestBase, support.TestCase):

    def _get_icoroutinefactory_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutineFactory

    def test_it_should_return_an_icoroutine_factory(self):
        icoroutinefactory_interface = self._get_icoroutinefactory_interface()
        filter_factory = self._call_sut()
        self.assert_interfaces(filter_factory, [icoroutinefactory_interface])

    def test_sink_factory_should_call_sink_from_callable(self):
        function = self._get_required_args()[0]
        sink_factory = self._call_sut(function)
        with mock.patch('m4us.core.coroutines.sink_from_callable') as \
          mock_sink_from_callable:
            sink_factory()
        mock_sink_from_callable.assert_called_once_with(function)

    def test_sink_factory_should_return_sink_from_callable_result(self):
        expected_result = 'sink_from_callable return value'
        sink_factory = self._call_sut()
        with mock.patch('m4us.core.coroutines.sink_from_callable') as \
          mock_sink_from_callable:
            mock_sink_from_callable.return_value = expected_result
            sink_coroutine = sink_factory()
        self.assert_is(sink_coroutine, expected_result)


class TestSinkShouldHaveCorrectSignatureAndDocstring(SinkTestBase,
  support.TestCase):

    def _get_required_args(self):
        return (filter_function,)

    def test_it_should_preserve_docstring(self):
        function = self._get_required_args()[0]
        filter_factory = self._call_sut()
        self.assert_equal(filter_factory.__doc__, function.__doc__)

    def test_it_should_call_strip_first_parameter(self):
        with mock.patch('m4us.core.utils._strip_first_parameter') as \
          mock_strip_first_parameter:
            self._call_sut()
        self.assert_true(mock_strip_first_parameter.called)

    def test_filter_factory_should_actualy_require_required_arguments(self):
        filter_factory = self._call_sut()
        with self.assert_raises(TypeError):
            filter_factory()
        with self.assert_not_raises(TypeError):
            filter_factory('required value')


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

if __name__ == '__main__':
    unittest2.main()
