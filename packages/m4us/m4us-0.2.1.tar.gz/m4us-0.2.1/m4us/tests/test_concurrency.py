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


"""Tests for m4us.concurrency."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import time
import Queue

#---  Third-party imports
import unittest2
import mock

#---  Project imports
from m4us.core.tests import test_coroutines, support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class ConcurrencyTestBase(support.CommonTestBase):

    @support.memoize
    def _get_coroutine(self):
        return test_coroutines.make_decorated_coroutine()()

    def _clear_get_coroutine_cache(self):
        if hasattr(self._get_coroutine.undecorated, 'cache'):
            del self._get_coroutine.undecorated.cache


#---  CoroutineThread tests

class CoroutineThreadTestBase(ConcurrencyTestBase):

    def _get_sut(self):
        from m4us import concurrency
        return concurrency._CoroutineThread

    def _get_required_args(self):
        return (self._get_coroutine(),) + self._get_queues()

    @support.memoize
    def _get_queues(self):
        in_queue = Queue.Queue()
        out_queue = Queue.Queue()
        return in_queue, out_queue

    def _clear_get_queues_cache(self):
        if hasattr(self._get_queues.undecorated, 'cache'):
            del self._get_queues.undecorated.cache

    def _get_messages(self):
        return (
          ('inbox', 'message 1'),
          ('inbox', 'message 2'),
        )

    def _make_shutdown_message(self):
        from m4us.core import messages
        return ('_thread_control', messages.Shutdown())

    def teardown(self):
        self._clear_get_coroutine_cache()
        self._clear_get_queues_cache()


class TestCoroutineThreadShouldAcceptPositionalArguments(
  CoroutineThreadTestBase, support.TestCase):

    def test_it_should_require_a_coroutine(self):
        with self.assert_raises(TypeError):
            self._get_sut()()

    def test_it_should_require_an_input_queue(self):
        coroutine = self._get_coroutine()
        with self.assert_raises(TypeError):
            self._call_sut(coroutine)

    def test_it_should_require_an_output_queue(self):
        coroutine = self._get_coroutine()
        in_queue = self._get_queues()[0]
        with self.assert_raises(TypeError):
            self._call_sut(coroutine, in_queue)


class TestCoroutineThreadShouldAcceptAndEmitMessages(CoroutineThreadTestBase,
  support.TestCase):

    def test_it_should_send_and_receive_queued_coroutine_messages(self):
        thread = self._call_sut()
        in_queue, out_queue = self._get_queues()
        messages = self._get_messages()
        shutdown_message = self._make_shutdown_message()
        thread.start()
        for message in messages:
            in_queue.put(message)
        in_queue.put(shutdown_message)
        thread.join()
        for message in messages:
            self.assert_equal(out_queue.get_nowait(), message)


class TestCoroutineThreadShouldSupportThrowingExceptions(
  CoroutineThreadTestBase, support.TestCase):

    def test_it_should_throw_queued_exceptions_to_the_coroutine(self):
        exception = support.DummyException()
        thread = self._call_sut()
        in_queue, out_queue = self._get_queues()
        primer_message = self._get_messages()[0]
        shutdown_message = self._make_shutdown_message()
        thread.start()
        in_queue.put(primer_message)
        in_queue.put(('_thread_exception', exception))
        in_queue.put(shutdown_message)
        thread.join()
        out_queue.get_nowait()  # Get the response to the primer message.
        self.assert_equal(out_queue.get_nowait(), ('exception', exception))


class TestCoroutineThreadShouldRespondToShutdownMessages(
  CoroutineThreadTestBase, support.TestCase):

    def test_it_should_shutdown_on_ishutdown_message(self):
        thread = self._call_sut()
        in_queue = self._get_queues()[0]
        shutdown_message = self._make_shutdown_message()
        self.assert_false(thread.is_alive())
        thread.start()
        self.assert_true(thread.is_alive())
        in_queue.put(shutdown_message)
        thread.join()
        self.assert_false(thread.is_alive())

    def test_it_should_close_coroutine_on_shutdown(self):
        thread = self._call_sut()
        coroutine = self._get_coroutine()
        in_queue = self._get_queues()[0]
        messages = self._get_messages()
        shutdown_message = self._make_shutdown_message()
        thread.start()
        for message in messages:
            in_queue.put(message)
        in_queue.put(shutdown_message)
        thread.join()
        with self.assert_raises(StopIteration):
            coroutine.send(messages[0])

    def test_it_should_shutdown_if_coroutine_shuts_down(self):
        in_queue, out_queue = self._get_queues()
        # This relies on the fact that coroutine_with_parameters dies after
        # it's second message.
        thread = self._call_sut(
          test_coroutines.make_coroutine_with_parameters()(1, 2), in_queue,
          out_queue)
        messages = self._get_messages()
        thread.start()
        for message in messages:  # Second message triggers StopIteration
            in_queue.put(message)
        thread.join()
        self.assert_false(thread.is_alive())


#---  ThreadedCoroutine tests

class ThreadedCoroutineTestBase(ConcurrencyTestBase,
  test_coroutines.BasicMessagesMixin, test_coroutines.CoroutineTestBase):

    def _get_sut(self):
        from m4us import concurrency
        return concurrency.ThreadedCoroutine

    def _get_required_args(self):
        return (self._get_coroutine(),)

    def _call_sut(self, *args, **kwargs):
        # Overridden
        coroutine = ConcurrencyTestBase._call_sut(self, *args, **kwargs)
        self._threaded_coroutines.append(coroutine)
        return coroutine

    def _get_messages(self):
        return (
          ('inbox', 'Hello'),
          ('inbox', 'Message 2'),
        )

    def _wait_for_message(self, coroutine, first_result):
        outbox_message = first_result
        for _ in xrange(100):
            if outbox_message is not None:
                break
            time.sleep(0.1)
            outbox_message = coroutine.send(('control', None))
        else:
            self.fail('Timed out waiting for coroutine to return a message.')
        return outbox_message

    def setup(self):
        ConcurrencyTestBase.setup(self)
        self._threaded_coroutines = []

    def teardown(self):
        for coroutine in self._threaded_coroutines:
            try:
                coroutine.close()
            except RuntimeError:
                pass
        del self._threaded_coroutines
        self._clear_get_coroutine_cache()


class TestThreadedCoroutineShouldProvideICoroutine(ThreadedCoroutineTestBase,
  test_coroutines.CoroutineShouldProvideICoroutine,
  support.ClassShouldProvideAndImplementInterface, support.TestCase):

    pass


class TestThreadedCoroutineShouldProvideINotLazy(ThreadedCoroutineTestBase,
  test_coroutines.CoroutineShouldProvideINotLazy,
  support.ClassShouldProvideAndImplementInterface, support.TestCase):

    pass


class TestThreadedCoroutineShouldAcceptAndEmitMessages(
  ThreadedCoroutineTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    def test_it_should_accept_and_emit_messages(self):
        # Overridden
        coroutine = self._call_sut()
        messages = self._get_messages()
        responses = self._get_responses()
        for message, response in zip(messages, responses):
            outbox_message = coroutine.send(message)
            outbox_message = self._wait_for_message(coroutine, outbox_message)
            self.assert_equal(outbox_message, response)

    def test_send_should_return_none_if_no_message_in_output_queue(self):
        coroutine = self._call_sut(start=False)
        message = self._get_messages()[0]
        self.assert_equal(coroutine.send(message), None)

    def test_senf_should_swallow_none_messages_to_lazy_coroutines(self):
        coroutine = self._call_sut()
        self.assert_equal(coroutine.send(('control', None)), None)


class TestThreadedCoroutineShouldSupportThrowingExceptions(
  ThreadedCoroutineTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    def test_throw_should_raise_unhandled_thrown_exception(self):
        # Overridden
        coroutine = self._call_sut()
        with self.assert_raises(support.DummyException):
            coroutine.throw(support.DummyException())
            for _ in xrange(100):
                time.sleep(0.1)
                coroutine.send(('control', None))

    def test_throw_should_return_yielded_results(self):
        exception = support.DummyException()
        coroutine = self._call_sut()
        primer_message = self._get_messages()[0]
        # We have to prime decorated_coroutine to get it in the while loop with
        # the exception handling.
        self._wait_for_message(coroutine, coroutine.send(primer_message))
        outbox_message = coroutine.throw(exception)
        outbox_message = self._wait_for_message(coroutine, outbox_message)
        self.assert_equal(outbox_message[1], exception)

    def test_throw_should_return_none_if_no_message_in_output_queue(self):
        coroutine = self._call_sut(start=False)
        self.assert_equal(coroutine.throw(support.DummyException()), None)


class TestThreadedCoroutineShouldSupportBeingClosed(ThreadedCoroutineTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestThreadedCoroutineShouldAcceptArguments(ThreadedCoroutineTestBase,
  support.TestCase):

    def test_it_should_require_a_coroutine_as_an_argument(self):
        with self.assert_raises(TypeError):
            self._get_sut()()

    def test_it_should_require_an_icoroutine_as_its_first_argument(self):
        with self.assert_raises(TypeError):
            self._call_sut(mock.Mock())

    def test_it_should_allow_limiting_the_input_queue_size(self):
        coroutine = self._call_sut(max_in_size=4)
        self.assert_equal(coroutine._in_queue.maxsize, 4)

    def test_it_should_allow_limiting_the_output_queue_size(self):
        coroutine = self._call_sut(max_out_size=17)
        self.assert_equal(coroutine._out_queue.maxsize, 17)

    def test_it_should_allow_the_thread_to_not_be_started_by_default(self):
        coroutine = self._call_sut(start=False)
        self.assert_false(coroutine._thread.is_alive())


class TestThreadedCoroutineShouldStartTheThread(ThreadedCoroutineTestBase,
  support.TestCase):

    def test_it_should_start_the_thread_by_default(self):
        coroutine = self._call_sut()
        self.assert_true(coroutine._thread.is_alive())

    def test_start_should_start_the_thread(self):
        coroutine = self._call_sut(start=False)
        self.assert_false(coroutine._thread.is_alive())
        coroutine.start()
        self.assert_true(coroutine._thread.is_alive())

    def test_start_should_raise_runtimeerror_if_thread_already_started(self):
        coroutine = self._call_sut()
        with self.assert_raises(RuntimeError):
            coroutine.start()


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
