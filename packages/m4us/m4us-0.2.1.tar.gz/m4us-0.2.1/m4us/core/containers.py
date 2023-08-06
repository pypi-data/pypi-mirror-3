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


"""Provides `components` that can contain and link other `components`.

Containers are `components` that contain other `components` and `coroutines`,
linking them in various ways.  These objects make it convenient to group
`coroutines` together to make larger reusable `components`.  The `coroutines`
contained within containers can be linked not only to each other, but to the
containers as well, allowing the containers externally to act like any other
`components`.

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
from m4us.core import components, utils, exceptions, interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class Graphline(components.Component):

    """Container `component` of `coroutines` with fully configurable `links`.

    This corresponds to Kamaelia_'s :class:`!Graphline` class.

    This class is useful for grouping several `coroutines` together, while
    still being able to specify special (i.e. non-standard) `links` among them.
    Where the :class:`Pipeline` class provides a strait linear linkage between
    it's `coroutines`, this class allows you to specify your own `links` as
    required.

    Only the `links` need to be specified.  The unique collection of
    `coroutines` will be automatically extracted from them.

    Additionally, if a `source` or `sink` is specified as ``'self'``, then a
    `link` will be created with the :class:`Graphline` instance.  This allows
    `messages` sent to the :class:`Graphline` instance to be forwarded on to
    the appropriate child `coroutine` and `messages` from a child to be sent
    out as the output from the :class:`Graphline`.  Note, however, that unlike
    regular `links`, when using ``'self'``, `links` should be `outbox` to
    `outbox` or `inbox` to `inbox`.  Kamaelia_ calls these types of `links`
    *pass-through linkages*.

    Example:

    >>> graphline = Graphline(
    ...   ('self', 'inbox', coroutine1, 'inbox'),
    ...   ('self', 'control', coroutine1, 'control'),
    ...   (coroutine1, 'outbox', coroutine2, 'inbox'),
    ...   (coroutine1, 'signal', coroutine2, 'control'),
    ...   (coroutine1, 'outbox', coroutine3, 'inbox'),
    ...   (coroutine1, 'signal', coroutine3, 'control'),
    ...   (coroutine2, 'outbox', 'self', 'outbox'),
    ...   (coroutine2, 'signal', 'self', 'signal'),
    ...   (coroutine3, 'outbox', 'self', 'outbox'),
    ...   (coroutine3, 'signal', 'self', 'signal'),
    ... )
    >>> scheduler.register(*graphline.coroutines)
    >>> post_office.register(*graphline.links)

    In this example, `messages` sent to *graphline* will be forwarded on to
    *coroutine1*.  `Messages` from *coroutine1* will be sent to both
    *coroutine2* and *coroutine3*.  And `messages` from both *coroutine2* and
    *coroutine3* will be forwarded out from *graphline*. This is a good example
    of non-standard `links`.

    Assuming there is a `producer` and a `consumer` connected to either side of
    the graphline, then visually, the above example looks like this:

    .. digraph:: graphline

        rankdir=LR
        producer -> graphline [ label = "1" ]
        graphline -> consumer [ label = "5" ]
        graphline -> coroutine1 [ label = "2" ]
        coroutine1 -> coroutine2 [ label = "3" ]
        coroutine1 -> coroutine3 [ label = "3" ]
        coroutine2 -> graphline [ label = "4" ]
        coroutine3 -> graphline [ label = "4" ]

    :param links: The `links` and `coroutines` to contain.  Each `link` should
      be in the form of :samp:`({source}, {outbox}, {sink}, {inbox})`.
    :type links: :class:`tuple` of 4-:class:`tuple`\s
    :param kwargs: Any keyword arguments will be set as attributes on the
      instance.
    :type kwargs: :class:`dict`

    :raises m4us.core.exceptions.InvalidLinkError: If an invalid `link`
      involving the :class:`Graphline`'s `mailboxes` is attempted.

    :Implements: :class:`~m4us.core.interfaces.ICoroutine` and
      :class:`~m4us.core.interfaces.IContainer`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory` and
      :class:`~m4us.core.interfaces.IContainerFactory`

    .. seealso:: The :class:`~m4us.core.interfaces.ICoroutine` and
        :class:`~m4us.core.interfaces.IContainer` `interfaces` for details on
        the methods and attributes provided by instances of this class.

    .. _Kamaelia: http://kamaelia.org

    """

    interface.implements(interfaces.IContainer)
    interface.classProvides(interfaces.IContainerFactory,
      interfaces.ICoroutineFactory)

    def __init__(self, *links, **kwargs):
        """See class docstring for this method's documentation."""
        components.Component.__init__(self, **kwargs)
        self.coroutines = self._get_coroutines_attribute(links)
        self.links = self._prepare_links(links)

    ## pylint: disable=R0201
    def _add_sub_container(self, coroutine, coroutines, coroutines_set):
        """If the `coroutine` is a `container`, add include it's children.

        If the `coroutine` is an
        :class:`m4us.core.interfaces.IContainer`, then it's `coroutines` are
        added to the :class:`list` and :class:`set` of `coroutines.

        :param coroutine: The `coroutine` to check.
        :type coroutine: :class:`ICoroutine`
        :param coroutines: Pre-existing list of `coroutines` to extend.
        :type coroutines: :class:`list`
        :param coroutines_set: Pre-existing set of `coroutines` to extend.
        :type coroutines_set: :class:`set`

        """
        container = interfaces.IContainer(coroutine, None)
        if container:
            for sub_coroutine in container.coroutines:
                if sub_coroutine not in coroutines_set:
                    coroutines.append(sub_coroutine)
                    coroutines_set.add(sub_coroutine)
    ## pylint: enable=R0201

    def _get_coroutines_attribute(self, links):
        """Extract and return the `coroutines` from the `links`.

        The `coroutines` are all unique `coroutines` from the given `links`,
        including the :class:`Graphline` instance.

        If any `coroutine` is also an
        :class:`m4us.core.interfaces.IContainer`, then it's `coroutines` are
        included automatically.

        :param links: The `post office` `links` given at instantiation.
        :type links: iterable of 4-:class:`tuple`'s

        """
        coroutines, coroutines_set = [self], set()
        for source, _, sink, _ in links:
            for coroutine in (source, sink):
                if coroutine != 'self' and coroutine not in coroutines_set:
                    coroutines.append(coroutine)
                    coroutines_set.add(coroutine)
                self._add_sub_container(coroutine, coroutines, coroutines_set)
        return tuple(coroutines)

    def _prepare_links(self, links):
        """Prepare and return the modified `links`.

        Any `links` that use ``'self'`` as the `source` or `sink` are converted
        to `links` to or from the :class:`Graphline` instance.

        :param links: The `post office` `links` given at instantiation.
        :type links: iterable of 4-:class:`tuple`'s

        If any `coroutine` is also an
        :class:`m4us.core.interfaces.IContainer`, then it's `links` are
        included automatically.

        :raises m4us.core.exceptions.InvalidLinkError: If an invalid `link`
          involving the :class:`Graphline`'s `mailboxes` is attempted.

        .. seealso:: The class's docstring for more details on how ``'self'``
            `links` are handled.

        """
        prepared_links = set()
        for source, outbox, sink, inbox in links:
            if source == 'self':
                if outbox in ('outbox', 'signal'):
                    ## pylint: disable=E1101
                    raise exceptions.InvalidLinkError(source_outbox=(source,
                      outbox), sink_inbox=(sink, inbox))
                    ## pylint: enable=E1101
                source = self
                if outbox == 'inbox':
                    outbox = '_outbox_to_child'
                elif outbox == 'control':
                    outbox = '_signal_to_child'
            if sink == 'self':
                if inbox in ('inbox', 'control'):
                    ## pylint: disable=E1101
                    raise exceptions.InvalidLinkError(source_outbox=(source,
                      outbox), sink_inbox=(sink, inbox))
                    ## pylint: enable=E1101
                sink = self
                if inbox == 'outbox':
                    inbox = '_inbox_from_child'
                elif inbox == 'signal':
                    inbox = '_control_from_child'
            prepared_links.add((source, outbox, sink, inbox))
            for coroutine in source, sink:
                if coroutine is self:
                    continue
                container = interfaces.IContainer(coroutine, None)
                if container:
                    prepared_links.update(container.links)
        return frozenset(prepared_links)

    ## pylint: disable=R0201
    def _main(self):
        """Forward incoming and outgoing `messages` to and from the children.

        `Messages` sent in to this class are passed on to the appropriate child
        `coroutines` and `messages` from configured child `coroutines` are sent
        out from this class.

        :returns: The container's `coroutine`.
        :rtype: :class:`~m4us.core.interfaces.ICoroutine`

        .. seealso:: The :meth:`m4us.core.interfaces.IComponent._main` method
            for more details on this method.

        """
        mailbox_map = {
          'control': '_signal_to_child',
          '_inbox_from_child': 'outbox',
          '_control_from_child': 'signal',
        }
        inbox, message = (yield)
        while True:
            outbox = mailbox_map.get(inbox, '_outbox_to_child')
            if utils.is_shutdown(outbox, message, 'signal'):
                yield outbox, message
                break
            inbox, message = (yield outbox, message)
    ## pylint: enable=R0201


class Pipeline(Graphline):

    """Container `component` of `coroutines` that `links` them in a pipeline.

    This corresponds to Kamaelia_'s :class:`!Pipeline` class.

    A pipeline consists of chaining each of the given `coroutines` together in
    order such that the ``outbox`` and ``signal`` `outboxes` of each
    `coroutine` are linked to the ``inbox`` and ``control`` `inboxes` of the
    next one.

    Additionally, the :class:`Pipeline`'s ``inbox`` and ``control`` `inboxes`
    are linked to the first `coroutine`'s ``inbox`` and ``control`` `inboxes`.
    Similarily, the :class:`Pipeline`'s ``outbox`` and ``signal`` `outboxes`
    are linked to the last `coroutine`'s ``outbox`` and ``signal`` `outboxes`.
    This means that the pipeline can be treated like any other `coroutine`,
    responding to incomming `messages` and emitting outgoing `messages`.

    Example:

    >>> pipeline = Pipeline(coroutine1, coroutine2, coroutine3)
    >>> scheduler.register(*pipeline.coroutines)
    >>> post_office.register(*pipeline.links)

    In this example, `messages` sent to *pipeline* will be forwarded on to
    *coroutine1*, who's `messages` will be sent to *coroutine2*, who's
    `messages` will be sent to *coroutine3*, who's `messages` will be forwarded
    out of *pipeline*.

    Assuming there is a `producer` and a `consumer` connected to either side of
    the pipeline, then visually, the above example looks like this:

    .. digraph:: pipeline

        rankdir=LR
        producer -> pipeline [ label = "1" ]
        pipeline -> consumer [ label = "6" ]
        pipeline -> coroutine1 [ label = "2" ]
        coroutine1 -> coroutine2 [ label = "3" ]
        coroutine2 -> coroutine3 [ label = "4" ]
        coroutine3 -> pipeline [ label = "5" ]

    :param first_coroutine: The first `coroutine` in the pipeline.  It will
      receive incomming `messages` to the pipeline.
    :type first_coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param other_coroutines: Any other `coroutines` in the pipeline, in order.
      `Messages` emmitted by the last one will be emitted by the pipeline.
    :type other_coroutines: :class:`tuple` of
      :class:`~m4us.core.interfaces.ICoroutine`\s
    :param kwargs: Like other `components`, any given keyword arguments will be
      set as instance attributes.
    :type kwargs: :class:`dict`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine` and
      :class:`~m4us.core.interfaces.IContainer`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory` and
      :class:`~m4us.core.interfaces.IContainerFactory`

    .. seealso:: The :class:`~m4us.core.interfaces.ICoroutine` and
        :class:`~m4us.core.interfaces.IContainer` `interfaces` for details on
        the methods and attributes provided by instances of this class.

    """

    interface.classProvides(interfaces.IContainerFactory,
      interfaces.ICoroutineFactory)

    def __init__(self, first_coroutine, second_coroutine, *other_coroutines,
      **kwargs):
        """See class docstring for this method's documentation."""
        self._initial_coroutines = ((first_coroutine, second_coroutine) +
          other_coroutines)
        links = self._build_links(first_coroutine, second_coroutine,
          *other_coroutines)
        ## pylint: disable=W0142
        Graphline.__init__(self, *links, **kwargs)
        ## pylint: enable=W0142

    ## pylint: disable=R0201
    def _build_links(self, *coroutines):
        """Construct and return the set of pipeline `links`.

        This method generates a set of `links` chaining all the given
        `coroutines` together in a pipeline.  The set of links is in the format
        that the :class:`Graphline` parent class accepts.

        Additionally, the class's ``inbox``, ``control``, ``outbox`` and
        ``signal`` `mailboxes` are linked to the first and last `coroutines`
        appropriately so that `messages` to and from the class itself are
        delivered as expected.

        :param coroutines: The `coroutines` to link together.
        :type coroutines: :class:`tuple` of
          :class:`~m4us.core.interfaces.ICoroutine`\s

        :returns: The collection of `links` to pass to the parent
          :class:`Graphline` class.
        :rtype: :class:`set` of link :class:`tuples`

        .. seealso:: The :class:`Graphline` class for details on the `link`
            format and the use of ``'self'`` in them.

        """
        links = utils.easy_link(*coroutines)
        links.update((
          ('self', 'inbox', coroutines[0], 'inbox'),
          ('self', 'control', coroutines[0], 'control'),
          (coroutines[-1], 'outbox', 'self', 'outbox'),
          (coroutines[-1], 'signal', 'self', 'signal'),
        ))
        return links
    ## pylint: enable=R0201

    def _get_coroutines_attribute(self, links):
        """Extract and return the `coroutines` in the `links`.

        This method has been overridden to handle sub-containers while still
        preserving the coroutine order as best as it can.

        :param links: The `post office` `links` given at instantiation.  *(Not
          used)*.
        :type links: iterable of 4-:class:`tuple`'s

        """
        coroutines, coroutines_set = [self], set()
        for coroutine in self._initial_coroutines:
            if coroutine not in coroutines_set:
                coroutines.append(coroutine)
                coroutines_set.add(coroutine)
            # This order is important.  sub_container coroutine should be
            # ordered immediately after the parent container to keep actual
            # execution order fair.
            self._add_sub_container(coroutine, coroutines, coroutines_set)
        return tuple(coroutines)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
