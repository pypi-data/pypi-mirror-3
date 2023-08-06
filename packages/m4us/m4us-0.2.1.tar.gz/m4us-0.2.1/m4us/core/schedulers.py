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


"""Provides a variety of `scheduler` classes to coordinate `coroutines`.

`Schedulers` are responsible for the main program loop, cycling through each
registered `coroutine` in turn.  They also send `post office` `messages` into
the registered `coroutines` and post emitted `messages` back to the `post
office`.

"""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import collections

#---  Third-party imports
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
from  . import messages, utils, exceptions, interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class Scheduler(object):

    """The standard `scheduler` class to run `coroutines`.

    This is a simple and reasonably efficient implementation of
    :class:`~m4us.core.interfaces.IScheduler`.  Unless you have a special need,
    this is this probably `scheduler` you want to use.

    :param post_office: The `post office` object to use for `message` routing.
    :type post_office: :class:`~m4us.core.interfaces.IPostOffice`

    :raises exceptions.TypeError: If the given `post office` does not provide
      or cannot be adapted to :class:`~m4us.core.interfaces.IPostOffice`.

    :Implements: :class:`~m4us.core.interfaces.IScheduler`
    :Provides: :class:`~m4us.core.interfaces.ISchedulerFactory`

    .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface` for
        details on `post offices`.

    """

    interface.implements(interfaces.IScheduler)
    interface.classProvides(interfaces.ISchedulerFactory)

    def __init__(self, post_office, add_ignores_duplicates=False,
      remove_ignores_missing=False):
        """See class docstring for this method's documentation."""
        # Raises TypeError if not adaptable to IPostOffice.
        interfaces.IPostOffice(post_office)
        self._post_office = post_office
        self._ignore_duplicates = add_ignores_duplicates
        self._ignore_missing = remove_ignores_missing
        # We use a deque for it's rotate() and popleft() (and remove() by
        # extension) which are more efficient than a regular list.
        self._run_queue = collections.deque()
        self._shutting_downs = set()

    def register(self, first_coroutine, *other_coroutines):
        """Register one or more `coroutines` with the `scheduler`.

        .. seealso:: The :class:`~m4us.core.interfaces.IScheduler` `interface`
            for details about this method.

        """
        for coroutine in (first_coroutine,) + other_coroutines:
            # Raise TypeError of not adaptable to ICoroutine
            interfaces.ICoroutine(coroutine)
            if coroutine in self._run_queue:
                if self._ignore_duplicates:
                    continue
                ## pylint: disable=E1101
                raise exceptions.DuplicateError(coroutine=coroutine)
                ## pylint: enable=E1101
            self._run_queue.append(coroutine)

    def unregister(self, first_coroutine, *other_coroutines):
        """Unregister one or more `coroutines` from the `scheduler`.

        .. seealso:: The :class:`~m4us.core.interfaces.IScheduler` `interface`
            for details about this method.

        """
        for coroutine in (first_coroutine,) + other_coroutines:
            try:
                self._run_queue.remove(coroutine)
            except ValueError:
                if self._ignore_missing:
                    continue
                ## pylint: disable=E1101
                raise exceptions.NotAddedError(coroutine=coroutine)
                ## pylint: enable=E1101
            coroutine.close()

    def step(self):
        """Run one `coroutine`.

        .. note:: `Coroutines` are run in a `round-robin`_ style, in the order
            that they have been added.  `Coroutines` should not, however, rely
            on this implementation detail.

        .. seealso:: The :class:`~m4us.core.interfaces.IScheduler` `interface`
            for details about this method.

        .. _`round-robin`: http://en.wikipedia.org/wiki/Round-robin_scheduling

        """
        # Note: It is assumed that either the original coroutine can store it's
        # state or that the same coroutine adapter is returned with every call
        # to ICoroutine.  It is the responsibility of the adapter and/or the
        # adapter registry to ensure the same adapted coroutine is returned.
        original_coroutine = self._run_queue[0]
        coroutine = interfaces.ICoroutine(original_coroutine)
        post_office = interfaces.IPostOffice(self._post_office)
        inbox_messages = self._get_inbox_messages(original_coroutine)
        try:
            for inbox_message in inbox_messages:
                ## pylint: disable=E1121
                outbox_message = coroutine.send(inbox_message)
                ## pylint: enable=E1121
                if outbox_message is None:
                    continue
                outbox, message = outbox_message
                # If the message is an IShutdown, the corutine should now be in
                # the "shutting down" state.
                if utils.is_shutdown(outbox, message, 'signal'):
                    self._shutting_downs.add(original_coroutine)
                try:
                    ## pylint: disable=E1121
                    post_office.post(original_coroutine, outbox, message)
                    ## pylint: enable=E1121
                ## pylint: disable=E1101
                except exceptions.NoLinkError:
                    ## pylint: enable=E1101
                    # If we get a NoLinkError and the message is an IShutdown,
                    # then we assume it is sent from a consumer and we drop it.
                    # If it is not an IShutdown, however, it is an error.
                    if not interfaces.IShutdown(message, False):
                        raise
        except StopIteration:
            self.unregister(original_coroutine)
            if original_coroutine in self._shutting_downs:
                self._shutting_downs.remove(original_coroutine)
        else:
            self._run_queue.rotate(-1)

    def _get_inbox_messages(self, original_coroutine):
        """Return an iterable of `inbox` `messages` waiting to be delivered.

        if the `coroutine` is shutting down, then only a single
        :class:`~m4us.core.interfaces.IShutdown` ``control`` `message` will be
        in the returned iterable.

        Otherwise, if there are any waiting `messages` in the `post office`,
        they will be returned.

        If there are no `post office` `messages` for the `coroutine`, and the
        `coroutine` is not `lazy`, then only a :obj:`None` ``control``
        `message` will be in the returned interable.

        :param original_coroutine: The (unadapted) `coroutine` for which to
          check for `messages`.  This should be the `coroutine` object as it
          was registered with the `post office`, not an adapter or anything.
        :type original_coroutine: :class:`~m4us.core.interfaces.ICoroutine`

        :returns: An iterable of `inbox` messages to be delivered to the given
          `coroutine`.
        :rtype: *iterable*

        :raises m4us.core.exceptions.NeverRunError: If the `post office` raises
          :exc:`~m4us.core.exceptions.NotASinkError` and the `coroutine` is
          `lazy`.

        """
        post_office = interfaces.IPostOffice(self._post_office)
        is_lazy = not interfaces.INotLazy(original_coroutine, False)
        if original_coroutine in self._shutting_downs:
            inbox_messages = (('control', messages.Shutdown()),)
            return inbox_messages
        try:
            ## pylint: disable=E1121
            inbox_messages = post_office.retrieve(original_coroutine)
            ## pylint: enable=E1121
        ## pylint: disable=E1101
        except exceptions.NotASinkError:
            ## pylint: enable=E1101
            # If we get a NotASinkError from PostOffice.retrieve, and the
            # coroutine is lazy, then it will never be run.
            if is_lazy:
                ## pylint: disable=E1101
                raise exceptions.NeverRunError(
                  coroutine=original_coroutine)
                ## pylint: enable=E1101
            # Otherwise, if it is not lazy, then we assume that it is a
            # producer and will be handled like any other non-lazy
            # coroutine.
            inbox_messages = ()
        # If a coroutine is not lazy and there are no messages, then we
        # send None to control instead.
        if not inbox_messages and not is_lazy:
            inbox_messages = (('control', None),)
        return inbox_messages

    def cycle(self):
        """Cycle once through the main loop, running all eligible `coroutines`.

        .. warning:: The current implementation of this method can handle a
            shrinking run queue due to `coroutines` shutting down, but it has
            not yet been designed to handle the dynamic adding or removing of
            `coroutines` within a the cycle execution.  It's behaviour in those
            situations is currently undefined.

        .. seealso:: The :class:`~m4us.core.interfaces.IScheduler` `interface`
            for details about this method.

        .. seealso:: The :meth:`step` method for details how the `coroutines`
            are run.

        """
        # TODO: Handle changes in _run_queue length?
        for _ in xrange(len(self._run_queue)):
            self.step()

    def run(self, cycles=None):
        """Start the `scheduler`, running all registered `coroutines`.

        .. warning:: If *cycles* is not specified and any of the `coroutines`
            do not cascade :class:`~m4us.core.interfaces.IShutdown` `messages`
            or shutdown properly, then this method will likely loop forever.

        .. seealso:: The :class:`~m4us.core.interfaces.IScheduler` `interface`
            for details about this method.

        .. seealso:: The :meth:`cycle` method for details how the `coroutines`
            are run.

        .. seealso:: The :class:`~m4us.core.interfaces.IShutdown` `interface`
            for details on shutdown messages.

        """
        if cycles is not None:
            for _ in xrange(cycles):
                self.cycle()
            return
        while self._run_queue:
            self.cycle()


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
