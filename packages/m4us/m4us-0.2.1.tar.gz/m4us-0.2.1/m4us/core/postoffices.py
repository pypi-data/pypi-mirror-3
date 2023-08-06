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


"""Provides various kinds of `post office` classes for `message` routing.

`Post offices` are responsible for receiving posted `messages` from
`coroutines` and routing them to message queues of other `coroutines` based on
the `links` that have been registered.

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

#---  Third-party imports
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
from m4us.core import exceptions, interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class PostOffice(object):

    """The standard `post office` class used for `message` routing.

    This is a simple and reasonably efficient implementation of
    :class:`~m4us.core.interfaces.IPostOffice`.  Unless you have a special
    need, this is this `post office` you want to use.

    :Implements: :class:`~m4us.core.interfaces.IPostOffice`
    :Provides: :class:`~m4us.core.interfaces.IPostOfficeFactory`

    """

    interface.implements(interfaces.IPostOffice)
    interface.classProvides(interfaces.IPostOfficeFactory)

    def __init__(self, link_ignores_duplicates=False,
      unlink_ignores_missing=False):
        """See class docstring for this method's documentation."""
        self._ignore_duplicates = link_ignores_duplicates
        self._ignore_missing = unlink_ignores_missing
        # Note: collections.defaultdict is not used here because keys should
        # not be added through casual querying, but only explicitly, like
        # through link() for example.
        self._links = {}
        self._message_queues = {}
        self._registered_sinks = set()

    def register(self, first_link, *other_links):
        """Register `links` between `coroutines`.

        .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface`
            for details about this method.

        """
        for source, outbox, sink, inbox in (first_link,) + other_links:
            source_outbox, sink_inbox = (source, outbox), (sink, inbox)
            if sink_inbox in self._links.setdefault(source_outbox, set()):
                if self._ignore_duplicates:
                    continue
                ## pylint: disable=E1101
                raise exceptions.LinkExistsError(link=sink_inbox)
                ## pylint: enable=E1101
            self._links[source_outbox].add(sink_inbox)
            self._message_queues.setdefault(sink, [])
            self._registered_sinks.add(sink)

    def unregister(self, first_link, *other_links):
        """Unregister previously registered `links`.

        .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface`
            for details about this method.

        """
        for source, outbox, sink, inbox in (first_link,) + other_links:
            source_outbox, sink_inbox = (source, outbox), (sink, inbox)
            try:
                self._links[source_outbox].remove(sink_inbox)
            except KeyError:
                if self._ignore_missing:
                    continue
                ## pylint: disable=E1101
                raise exceptions.NoLinkError(source_outbox=source_outbox,
                  sink_inbox=sink_inbox)
                ## pylint: enable=E1101
            if not self._links[source_outbox]:
                del self._links[source_outbox]
            # If no sources use the sink anymore, unregister it.
            self._registered_sinks = set(sink for source_outbox in self._links
              for sink, _ in self._links[source_outbox])

    def post(self, source, outbox, message):
        """Post a `message` from the `source` `outbox`.

        .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface`
            for details about this method.

        """
        source_outbox = (source, outbox)
        if source_outbox not in self._links:
            ## pylint: disable=E1101
            raise exceptions.NoLinkError('The source/outbox '
              '"{source_outbox!r}" has not been linked.',
              source_outbox=source_outbox)
            ## pylint: enable=E1101
        for sink, inbox in self._links[source_outbox]:
            self._message_queues[sink].append((inbox, message))

    def retrieve(self, sink):
        """Retrieve all outstanding `messages` for a `sink` `coroutine`.

        .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface`
            for details about this method.

        """
        try:
            messages = self._message_queues[sink]
        except KeyError:
            ## pylint: disable=E1101
            raise exceptions.NotASinkError(coroutine=sink)
            ## pylint: enable=E1101
        # If the component has been unregistered, remove it's message queue.
        if sink not in self._registered_sinks:
            del self._message_queues[sink]
        else:
            # Note: We replace the message queue with a new empty one so that
            # the existing messages can be processed as a batch, but that any
            # new messages that come in will be handled the next time
            # retrieve() is called.  This ensures that the returned
            # messages iterable is always of finite length, preventing
            # infinite looping.
            self._message_queues[sink] = []
        return messages


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
