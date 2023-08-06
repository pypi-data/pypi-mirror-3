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


"""Provides support for concurrent execution of `coroutines`."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import threading
import Queue

#---  Third-party imports
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
from m4us.core import api as core
from m4us import interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class _CoroutineThread(threading.Thread):

    """Thread that can run a `coroutine` using `message` queues.

    This class' :meth:`run` method is designed to run a `coroutine`, delivering
    `messages` between the `coroutine` and the `message` queues.

    :param coroutine: The `coroutine` to run in it's own thread.
    :type coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param in_queue: The input queue of `messages` to send to the `coroutine`.
    :type in_queue: :class:`~Queue.Queue`
    :param out_queue: The output queue of `message` sent from the `coroutine`.
    :type out_queue: :class:`~Queue.Queue`

    """

    def __init__(self, coroutine, in_queue, out_queue):
        """See class docstring for this method's documentation."""
        threading.Thread.__init__(self)
        self._coroutine = coroutine
        self._in_queue, self._out_queue = in_queue, out_queue

    def run(self):
        """Send and receive `coroutine` `messages`.

        This is the main loop inside the thread.  `Messages` put on the input
        queue will be sent to the `coroutine` and it's responses will be put on
        the output queue.

        All incoming `messages` are expected to be in the standard form of
        :samp:`({inbox}, {message})`.

        If an :class:`~m4us.core.interfaces.IShutdown` message is sent in on
        the ``_thread_control`` `inbox`, the `coroutine` will be closed and the
        thread will be shut down.

        To have an exception thrown into the `coroutine`, send it as a
        `message` on the ``_thread_exception`` inbox.

        Any exceptions raised by the `coroutine` will be put on the output
        queue in the ``_thread_exception`` `outbox` and the thread will shut
        down.

        .. note:: The thread only runs if there are `messages` in the input
            queue, regardless of whether or not the `coroutine` is `lazy`.  It
            is expected that ``('control', None)`` `messages` will be sent to
            non-`lazy` `coroutines` in order to make them run every cycle.

        .. seealso:: The :class:`~m4us.core.interfaces.INotLazy` `interface`
            for details on non-`lazy` `coroutines`.

        """
        while True:
            inbox, message = self._in_queue.get()
            try:
                if core.is_shutdown(inbox, message, '_thread_control'):
                    self._coroutine.close()
                    break
                try:
                    if inbox == '_thread_exception':
                        outbox_message = self._coroutine.throw(message)
                    else:
                        outbox_message = self._coroutine.send((inbox, message))
                ## pylint: disable=W0703
                except Exception as error:
                    ## pylint: enable=W0703
                    self._out_queue.put(('_thread_exception', error))
                    break
                self._out_queue.put(outbox_message)
            finally:
                self._in_queue.task_done()


class ThreadedCoroutine(object):

    """Wrapper that runs a `coroutine` in a separate thread.

    This class is an analog to Kamaelia_'s :class:`!ThreadedComponent` class
    but is meant to be used on any `coroutine` or `component`.

    This class uses thread-safe queues for `message` and exception delivery.
    Method calls on this class will always return immediately, merely queueing
    up `messages` to be delivered to and from the given `coroutine`.  The
    exception is when either of the queue sizes are set and the queue is full.
    In that case, a method will hang until room becomes available in the queue.

    :param coroutine: The `coroutine` to run in it's own thread.
    :type coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param max_in_size: The maximum input queue size.  ``0`` means unlimited.
    :type max_in_size: :class:`int`
    :param max_out_size: The maximum output queue size.  ``0`` means unlimited.
    :type max_out_size: :class:`int`
    :param start: Whether or not to automatically start the thread.  If
      disabled, the :meth:`start` method must be called explicitly.
    :type start: :class:`bool`

    :Implements: :class:`~m4us.interfaces.IThreadedCoroutine` and
      :class:`~m4us.core.interfaces.INotLazy`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    Example usage:

    >>> scheduler.register(ThreadedCoroutine(my_coroutine()))

    .. seealso:: The Python_ :class:`~Queue.Queue` class for more information
        on limiting queue sizes.

    .. _Kamaelia: http://kamaelia.org
    .. _Python: http://python.org

    """

    interface.implements(interfaces.IThreadedCoroutine, core.INotLazy)
    interface.classProvides(core.ICoroutineFactory)

    ## pylint: disable=W0105
    _closed = False
    """Indicates whether or not instances of this class have been closed.

    :type: :class:`bool`

    .. seealso:: The :meth:`close` method for details.

    """
    ## pylint: enable=W0105

    def __init__(self, coroutine, max_in_size=0, max_out_size=0, start=True):
        """See class docstring for this method's documentation."""
        self._coroutine = core.ICoroutine(coroutine)
        self._in_queue = Queue.Queue(max_in_size)
        self._out_queue = Queue.Queue(max_out_size)
        self._thread = _CoroutineThread(coroutine, self._in_queue,
          self._out_queue)
        if start:
            self.start()

    def _get_queued_message(self):
        """Try to return a queued output `message`.

        This method tries to retrieve and return a `message` from the output
        queue without blocking.  If there is no `message` waiting, :obj:`None`
        is returned.

        If an exception is received on the ``_thread_exception`` `outbox`, the
        exception is raised.

        :returns: A queued up output `message`, if one exists.
        :rtype: 2-:class:`tuple` or :obj:`None`

        :raises: Any queued up exceptions coming from the `coroutine`.

        """
        try:
            message = self._out_queue.get_nowait()
        except Queue.Empty:
            return None
        if message is not None:
            inbox, error = message
            if inbox == '_thread_exception':
                raise error
        self._out_queue.task_done()
        return message

    def start(self):
        """Start the `coroutine` thread if it needs explicit starting.

        .. seealso:: :class:`~m4us.interfaces.IThreadedCoroutine` for details
            about this method.

        .. seealso:: This class's docstring for details about the implicit and
            explicit starting of the `coroutine` thread.

        """
        self._thread.start()

    def send(self, message):
        """Send and receive `messages` to and from the `coroutine`.

        .. note:: ``('control', None)`` `inbox` `messages` will only be sent to
            the `coroutine` if it is not `lazy` (i.e. it provides the
            :class:`~m4us.core.interfaces.INotLazy` marker `interface`).

        .. note:: Any `message` returned will be the next one in the output
            queue, and not necessarily the immediate response to the given
            `message` when sent.

        .. seealso:: :class:`~m4us.core.interfaces.ICoroutine` for details
            about this method.

        """
        if self._closed:
            raise StopIteration()
        if message != ('control', None) or core.INotLazy(self._coroutine,
          False):
            self._in_queue.put(message)
        return self._get_queued_message()

    def throw(self, exception):
        """Throw an exception inside the threaded `coroutine`.

        .. note:: The thrown exception is queued up, in order, with other sent
            `messages` and so the threaded `coroutine` may not react to it
            immediately.

        .. note:: Like the :meth:`send` method, any `message` returned will be
            the next one in the output queue, and not necessarily the
            immediate response given exception.  This includes the raising of
            any handled exceptions.

        .. seealso:: :class:`~m4us.core.interfaces.ICoroutine` for details
            about this method.

        """
        if self._closed:
            raise exception
        self._in_queue.put(('_thread_exception', exception))
        return self._get_queued_message()

    def close(self):
        """Close the `coroutine` and shutdown it's thread.

        .. seealso:: :class:`~m4us.core.interfaces.ICoroutine` for details
            about this method.

        """
        if self._closed:
            return
        self._in_queue.put(('_thread_control', core.Shutdown()))
        self._thread.join()
        self._closed = True


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
