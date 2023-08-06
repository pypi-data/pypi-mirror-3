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


"""Tests for m4us.core.schedulers."""


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
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611


#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class SchedulerTestBase(support.CommonTestBase):

    def _get_ipostoffice_interface(self):
        from m4us.core import interfaces
        return interfaces.IPostOffice

    def _get_icoroutine_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutine

    def _get_inotlazy_interface(self):
        from m4us.core import interfaces
        return interfaces.INotLazy

    def _get_ishutdown_interface(self):
        from m4us.core import interfaces
        return interfaces.IShutdown

    def _get_notasinkerror_class(self):
        from m4us.core import exceptions
        return exceptions.NotASinkError

    def _get_nolinkerror_class(self):
        from m4us.core import exceptions
        return exceptions.NoLinkError

    def _get_neverrunerror_class(self):
        from m4us.core import exceptions
        return exceptions.NeverRunError

    def _get_messages(self):
        return (('inbox', 'Message 1'), ('inbox', 'Message 2'))

    def _make_shutdown_message(self):
        from m4us.core import messages
        return messages.Shutdown()

    def _make_mock_post_office(self):
        post_office = mock.Mock()
        ipostoffice_interface = self._get_ipostoffice_interface()
        interface.directlyProvides(post_office, ipostoffice_interface)
        # By default, retrieve will signal everything as a producer
        not_a_sink_error = self._get_notasinkerror_class()()
        post_office.retrieve.side_effect = not_a_sink_error
        return post_office

    def _make_mock_coroutine(self, lazy=False):
        # By default the mock coroutine will be a producer and so not lazy.
        coroutine = mock.Mock()
        icoroutine_interface = self._get_icoroutine_interface()
        provided_interfaces = [icoroutine_interface]
        if not lazy:
            inotlazy_interface = self._get_inotlazy_interface()
            provided_interfaces.append(inotlazy_interface)
        interface.directlyProvides(coroutine, *provided_interfaces)
        # By default, send will not return any messages.
        coroutine.send.return_value = None
        return coroutine

    def _make_mock_coroutines(self, count):
        return [self._make_mock_coroutine() for _ in xrange(count)]

    def _make_mock_shutting_down_coroutine(self):
        coroutine = self._make_mock_coroutine()
        shutdown_message = self._make_shutdown_message()
        coroutine.send.return_value = ('signal', shutdown_message)
        return coroutine

    def assert_mock_coroutine_sent_ishutdown(self, coroutine):
        ishutdown_interface = self._get_ishutdown_interface()
        call_args = coroutine.send.call_args[0]
        self.assert_equal(call_args[0][0], 'control')
        self.assert_true(ishutdown_interface(call_args[0][1], False))


class SchedulerShouldProvideIScheduler(
  support.ClassShouldProvideAndImplementInterface):

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.ISchedulerFactory,)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IScheduler,)

    def test_factory_should_accept_an_ipostoffice(self):
        post_office = self._make_mock_post_office()
        with self.assert_not_raises(TypeError):
            self._call_sut(post_office)

    def test_is_should_raise_typerrror_if_no_post_office_given(self):
        kwargs = self._get_required_kwargs()
        with self.assert_raises(TypeError):
            self._get_sut()(**kwargs)

    def test_it_should_raise_typerror_if_given_a_non_ipostoffice(self):
        with self.assert_raises(TypeError):
            self._call_sut()(mock.Mock())

    def test_it_should_accept_argument_add_ignores_duplicates(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(add_ignores_duplicates=True)

    def test_it_should_accept_argument_remove_ignores_missing(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(remove_ignores_missing=True)


class SchedulerShouldSupportAddingCoroutines(SchedulerTestBase):

    def _get_duplicateerror_class(self):
        from m4us.core import exceptions
        return exceptions.DuplicateError

    def test_add_should_accept_a_single_icoroutine_argument(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        with self.assert_not_raises(TypeError):
            scheduler.register(coroutine)

    def test_add_should_accept_multiple_icoroutines_in_one_call(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(4)
        with self.assert_not_raises(TypeError):
            scheduler.register(*coroutines)

    def test_add_should_raise_duplicateerror_if_coroutine_already_added(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        duplicate_error_class = self._get_duplicateerror_class()
        with self.assert_raises(duplicate_error_class):
            scheduler.register(coroutine, coroutine)

    def test_add_should_raise_typeerror_if_given_a_non_icoroutine(self):
        scheduler = self._call_sut()
        with self.assert_raises(TypeError):
            scheduler.register(mock.Mock())

    def test_add_should_not_raise_duplicateerror_if_add_is_idempotent(self):
        scheduler = self._call_sut(add_ignores_duplicates=True)
        coroutine = self._make_mock_coroutine()
        duplicate_error_class = self._get_duplicateerror_class()
        with self.assert_not_raises(duplicate_error_class):
            scheduler.register(coroutine, coroutine)


class SchedulerShouldSupportRemovingCoroutines(SchedulerTestBase):

    def _get_notaddederror_class(self):
        from m4us.core import exceptions
        return exceptions.NotAddedError

    def test_remove_should_accept_a_single_icoroutine_argument(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        with self.assert_not_raises(TypeError):
            scheduler.unregister(coroutine)

    def test_remove_should_accept_multiple_icoroutines_in_one_call(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(4)
        scheduler.register(*coroutines)
        with self.assert_not_raises(Exception):
            scheduler.unregister(*coroutines)

    def test_remove_should_close_coroutines(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        scheduler.unregister(coroutine)
        self.assert_true(coroutine.close.called)

    def test_remove_should_raise_notaddederror_if_coroutine_not_added(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        not_added_error_class = self._get_notaddederror_class()
        with self.assert_raises(not_added_error_class):
            scheduler.unregister(coroutine)

    def test_remove_should_not_raise_notaddederror_if_remove_is_idempotent(
      self):
        scheduler = self._call_sut(remove_ignores_missing=True)
        coroutine = self._make_mock_coroutine()
        not_added_error_class = self._get_notaddederror_class()
        with self.assert_not_raises(not_added_error_class):
            scheduler.unregister(coroutine)


class SchedulerShouldPostAndDeliverMessages(SchedulerTestBase):

    def test_step_should_send_messages_to_the_post_office(self):
        post_office = self._make_mock_post_office()
        scheduler = self._call_sut(post_office)
        coroutine = self._make_mock_coroutine()
        coroutine.send.return_value = ('outbox', 'Message')
        scheduler.register(coroutine)
        scheduler.step()
        expected_result = (coroutine, 'outbox', 'Message')
        self.assert_equal(post_office.post.call_args[0], expected_result)

    def test_step_should_send_all_post_office_messages_to_a_coroutine(self):
        post_office = self._make_mock_post_office()
        post_office.retrieve.side_effect = None
        messages = self._get_messages()
        post_office.retrieve.return_value = messages
        scheduler = self._call_sut(post_office)
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        scheduler.step()
        self.assert_equal(coroutine.send.call_count, 2)
        for call_args, expected_message in zip(coroutine.send.call_args_list,
          messages):
            self.assert_equal(call_args[0], (expected_message,))

    def test_step_should_send_none_if_no_messages_and_not_lazy(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        scheduler.step()
        inbox, message = coroutine.send.call_args[0][0]
        self.assert_equal(inbox, 'control')
        self.assert_is_none(message)

    def test_step_should_drop_received_nones(self):
        post_office = self._make_mock_post_office()
        scheduler = self._call_sut(post_office)
        # Default behaviour of mock coroutine is to return None.
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        for _ in xrange(10):
            scheduler.step()
        self.assert_false(post_office.post.called)


class SchedulerShouldBreakOnInvalidConfiguration(SchedulerTestBase):

    def test_step_should_raise_neverrunerror_if_not_a_sink_and_lazy(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine(lazy=True)
        scheduler.register(coroutine)
        neverrunerror_class = self._get_neverrunerror_class()
        with self.assert_raises(neverrunerror_class):
            scheduler.step()

    def test_step_should_pass_on_nolinkerror_from_post_office_post(self):
        post_office = self._make_mock_post_office()
        no_link_error_class = self._get_nolinkerror_class()
        no_link_error = no_link_error_class()
        post_office.post.side_effect = no_link_error
        coroutine = self._make_mock_coroutine()
        coroutine.send.return_value = ('outbox', 'Message')
        scheduler = self._call_sut(post_office)
        scheduler.register(coroutine)
        with self.assert_raises(no_link_error_class):
            scheduler.step()


class SchedulerShouldHandleCoroutineShutdowns(SchedulerTestBase):

    def test_step_should_drop_unpostable_ishutdown_messages(self):
        post_office = self._make_mock_post_office()
        no_link_error_class = self._get_nolinkerror_class()
        no_link_error = no_link_error_class()
        post_office.post.side_effect = no_link_error
        scheduler = self._call_sut(post_office)
        coroutine = self._make_mock_shutting_down_coroutine()
        scheduler.register(coroutine)
        with self.assert_not_raises(no_link_error_class):
            scheduler.step()

    def test_step_should_flag_a_coroutine_as_shutting_down_on_ishutdown(self):
        # This test is defined as it is part of the IScheduler interface, but
        # the actual requirement is implementation-specific.
        raise NotImplementedError

    def test_step_should_send_ishutdowns_to_coroutine_until_it_exits(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_shutting_down_coroutine()
        scheduler.register(coroutine)
        scheduler.step()
        self.assert_equal(coroutine.send.call_args[0][0], ('control', None))
        coroutine.send.return_value = None
        for _ in xrange(10):
            scheduler.step()
            self.assert_mock_coroutine_sent_ishutdown(coroutine)

    def test_step_should_not_send_post_office_messages_to_shutting_downs(self):
        post_office = self._make_mock_post_office()
        scheduler = self._call_sut(post_office)
        coroutine = self._make_mock_shutting_down_coroutine()
        scheduler.register(coroutine)
        self.assert_not_in(coroutine, scheduler._shutting_downs)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)
        post_office.retrieve.side_effect = None
        messages = self._get_messages()
        post_office.retrieve.return_value = messages
        scheduler.step()
        self.assert_mock_coroutine_sent_ishutdown(coroutine)
        # Coroutine should be sent ('control', None) first, then ('control',
        # Shutdown()).  If post office messages had been sent, then
        # call_args_list would be 3 since there are 2 messages in messages
        # waiting to be delivered.
        self.assert_equal(len(coroutine.send.call_args_list), 2)
        # If post office messages had been sent, then
        # post_office.retrieve.call_count would be 2, once for the ('control',
        # None) message, and then second for the messages.
        self.assert_equal(post_office.retrieve.call_count, 1)


class SchedulerShouldSupportCyclingAFixedNumberOfLoops(SchedulerTestBase):

    def test_cycle_should_run_once_through_all_coroutines(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(5)
        scheduler.register(*coroutines)
        for index, coroutine in enumerate(coroutines):
            self.assert_false(coroutine.send.called,
              'Coroutine {0} already called.'.format(index))
        scheduler.cycle()
        for index, coroutine in enumerate(coroutines):
            self.assert_true(coroutine.send.called,
              'Coroutine {0} not called.'.format(index))

    def test_run_should_support_running_a_fixed_number_of_cycles(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(5)
        scheduler.register(*coroutines)
        for coroutine in coroutines:
            self.assert_false(coroutine.send.called)
        scheduler.run(10)
        for coroutine in coroutines:
            self.assert_equal(coroutine.send.call_count, 10)


class SchedulerShouldSupportRunningUntilAllCoroutinesShutdown(
  SchedulerTestBase):

    def test_run_should_run_until_all_coroutines_terminate(self):
        # Note: This test kind of relies on scheduler.run() hanging on failure.
        #       As such, it's not a great implementation of the test.  A better
        #       way might be to run scheduler.run() with a timeout of some
        #       kind, but that would probably mean running it in a thread.
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(15)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.register(*coroutines)
        for coroutine in coroutines:
            self.assert_false(coroutine.send.called)
        scheduler.run()
        for coroutine in coroutines:
            self.assert_true(coroutine.send.called)


#-- Scheduler tests

class SchedulerClassTestBase(SchedulerTestBase):

    def _get_sut(self):
        from m4us.core import schedulers
        return schedulers.Scheduler

    def _get_required_args(self):
        return (self._make_mock_post_office(),)


class TestSchedulerClassShouldProvideIScheduler(SchedulerClassTestBase,
  SchedulerShouldProvideIScheduler, support.TestCase):

    pass


class TestSchedulerClassShouldSupportAddingCoroutines(SchedulerClassTestBase,
  SchedulerShouldSupportAddingCoroutines, support.TestCase):

    def test_add_should_add_icoroutines_to_its_run_queue(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)


class TestSchedulerClassShouldSupportRemovingCoroutines(SchedulerClassTestBase,
  SchedulerShouldSupportRemovingCoroutines, support.TestCase):

    def test_remove_should_remove_coroutines(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)
        scheduler.unregister(coroutine)
        self.assert_not_in(coroutine, scheduler._run_queue)


class TestSchedulerClassShouldPostAndDeliverMessages(SchedulerClassTestBase,
  SchedulerShouldPostAndDeliverMessages, support.TestCase):

    pass


class TestSchedulerClassShouldBreakOnInvalidConfiguration(
  SchedulerClassTestBase, SchedulerShouldBreakOnInvalidConfiguration,
  support.TestCase):

    pass


class TestSchedulerClassShouldHandleCoroutineShutdowns(SchedulerClassTestBase,
  SchedulerShouldHandleCoroutineShutdowns, support.TestCase):

    def test_step_should_flag_a_coroutine_as_shutting_down_on_ishutdown(self):
        # Overridden method.
        scheduler = self._call_sut()
        coroutine = self._make_mock_shutting_down_coroutine()
        scheduler.register(coroutine)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)

    def test_step_should_remove_terminated_coroutines_from_the_run_queue(self):
        coroutine = self._make_mock_coroutine()
        coroutine.send.side_effect = StopIteration
        scheduler = self._call_sut()
        scheduler.register(coroutine)
        self.assert_in(coroutine, scheduler._run_queue)
        scheduler.step()
        self.assert_not_in(coroutine, scheduler._run_queue)

    def test_step_should_remove_exited_coroutines_from_shutting_downs(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_shutting_down_coroutine()
        scheduler.register(coroutine)
        scheduler.step()
        self.assert_in(coroutine, scheduler._shutting_downs)
        coroutine.send.side_effect = StopIteration
        scheduler.step()
        self.assert_not_in(coroutine, scheduler._shutting_downs)
        self.assert_not_in(coroutine, scheduler._run_queue)


class TestSchedulerClassShouldSupportCyclingAFixedNumberOfLoops(
  SchedulerClassTestBase, SchedulerShouldSupportCyclingAFixedNumberOfLoops,
  support.TestCase):

    pass


class TestSchedulerClassShouldSupportRunningUntilAllCoroutinesShutdown(
  SchedulerClassTestBase,
  SchedulerShouldSupportRunningUntilAllCoroutinesShutdown, support.TestCase):

    def assert_in_run_queue(self, scheduler, *coroutines):
        for index, coroutine in enumerate(coroutines):
            self.assert_in(coroutine, scheduler._run_queue,
              'Coroutine {0} not in the run queue.'.format(index))

    def test_cycle_should_handle_a_shrinking_run_queue(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(7)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.register(*coroutines)
        self.assert_in_run_queue(scheduler, *coroutines)
        scheduler.cycle()
        self.assert_equal(len(scheduler._run_queue), 0)

    def test_run_should_run_until_run_queue_is_empty(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(15)
        for coroutine in coroutines:
            coroutine.send.side_effect = StopIteration
        scheduler.register(*coroutines)
        self.assert_in_run_queue(scheduler, *coroutines)
        scheduler.run()
        self.assert_equal(len(scheduler._run_queue), 0)


class SchedulerClassShouldCycleThroughCoroutines(SchedulerClassTestBase,
  support.TestCase):

    def test_step_should_cycle_the_to_next_coroutine(self):
        scheduler = self._call_sut()
        coroutines = self._make_mock_coroutines(3)
        scheduler.register(*coroutines)
        self.assert_items_equal(coroutines, scheduler._run_queue)
        for _ in xrange(10):
            scheduler.step()
            coroutines.append(coroutines.pop(0))
            self.assert_equal(coroutines, list(scheduler._run_queue))


class TestSchedulerClassGetInboxMessages(SchedulerClassTestBase,
  support.TestCase):

    def test_it_should_return_all_messages_for_coroutine(self):
        post_office = self._make_mock_post_office()
        post_office.retrieve.side_effect = None
        messages = self._get_messages()
        post_office.retrieve.return_value = messages
        scheduler = self._call_sut(post_office)
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        inbox_messages = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(inbox_messages), 2)
        for message, expected_message in zip(inbox_messages, messages):
            self.assert_equal(message, expected_message)

    def test_it_should_return_none_if_no_message_and_not_lazy(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        messages = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(messages), 1)
        inbox, message = messages[0]
        self.assert_equal(inbox, 'control')
        self.assert_is_none(message)

    def test_it_should_raise_neverrunerror_if_notasinkerror_and_lazy(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine(lazy=True)
        scheduler.register(coroutine)
        never_run_error_class = self._get_neverrunerror_class()
        with self.assert_raises(never_run_error_class):
            scheduler._get_inbox_messages(coroutine)

    def test_it_should_return_ishutdown_if_shutting_down(self):
        scheduler = self._call_sut()
        coroutine = self._make_mock_coroutine()
        scheduler.register(coroutine)
        scheduler._shutting_downs.add(coroutine)
        messages = scheduler._get_inbox_messages(coroutine)
        self.assert_equal(len(messages), 1)
        inbox, message = messages[0]
        self.assert_equal(inbox, 'control')
        ishutdown_interface = self._get_ishutdown_interface()
        self.assert_true(ishutdown_interface(message, False))


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

if __name__ == '__main__':
    unittest2.main()
