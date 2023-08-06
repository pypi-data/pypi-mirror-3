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


"""Provides the `interface` definitions for all important core objects."""

## pylint: disable=E0211,R0903,E0213,W0232


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


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Messages interfaces

class IMessageFactory(interface.Interface):

    """`Interface` for `callables` that return :class:`IMessage` objects."""

    def __call__(**kwargs):
        """Return the desired `message`.

        The `callable` should only be called with keyword arguments.

        :param kwargs: Keywords arguments to pass to the `factory` `callable`.
        :type kwargs: :class:`dict`

        :returns: The desired `message` object.
        :rtype: :class:`IMessage`

        .. note:: All unrecognized keyword arguments should be set as
            attributes on the :class:`IMessage` object.

        """


class IMessage(interface.Interface):

    """`Interface` for special `messages` passed between `coroutines`."""


class IShutdown(IMessage):

    """`Interface` for `messages` that tell `coroutines` to shutdown.

    Upon receipt of an :class:`IShutdown` `message`, `coroutines` should clean
    up any loose ends, forward on the :class:`IShutdown` `message` on it's
    ``signal`` `outbox` and then shutdown.

    """


class IProducerFinished(IShutdown):

    """`Interface` for `messages` signalling that a `producer` is done."""


#---  Coroutines interfaces

class ICoroutineFactory(interface.Interface):

    """`Interface` for `callables` that return :class:`ICoroutine` objects."""

    def __call__(*args, **kwargs):
        """Return the desired `coroutine`.

        :param args: Any arguments to pass to the `factory` `callable`.
        :type args: :class:`tuple`
        :param kwargs: Keywords arguments to pass to the `factory` `callable`.
        :type kwargs: :class:`dict`

        :returns: The desired `coroutine`.
        :rtype: :class:`ICoroutine`

        """


class ICoroutine(interface.Interface):

    """`Interface` that defines a Python_ `coroutine`.

    Python_ `coroutines` are defined in :PEP:`342`.

    .. note:: While Python_ `coroutines` are an extension of `generators`, and
        as such define a ``next()`` method, this `interface` does not include
        the ``next()`` method as it really only makes sense in the context of
        actual `generators` rather than for `coroutines`.

    .. note:: By default, all Python_ `coroutines` (i.e.
        :class:`~types.GeneratorType`) have been automatically configured to
        provide :class:`ICoroutine`.  This makes working with Python_
        `coroutines` more natural.

    .. _Python: http://python.org/

    """

    def send(message):
        """Send the `message` to the `coroutine`.

        :param message: The `message` object to send into the `coroutine`.  For
          this project it will normally be a 2-:class:`tuple` of the `inbox`
          and the `message`.
        :type message: :class:`object`

        :returns: Any `message` :keyword:`yield`\ed by the `coroutine`.  For
          this project it will normally be a 2-:class:`tuple` of the `outbox`
          and the `message`.
        :rtype: :class:`object`

        :raises exceptions.StopIteration: If the `coroutine` has terminated,
          either by :keyword:`return`\ing (as opposed to :keyword:`yield`\ing)
          or because the :meth:`close` method was called.

        .. note:: The first call to this method must pass :obj:`None` as the
            sole argument. This activates the `coroutine`.  The response from
            the first call is undefined.

        """

    def throw(exception):
        """Send the exception to the `coroutine`.

        The `coroutine` is expected to raise the exception in it's context at
        the reception point.  It may then catch it and handle it or not.

        :param exception: The exception to send to the `coroutine`.
        :type exception: :class:`Exception`

        :returns: If the exception is caught, then any `message`
          :keyword:`yield`\ed by the `coroutine`.
        :rtype: :class:`object`

        :raises: Any uncaught exception passed in via this method.

        """

    def close():
        """Terminate the `coroutine`.

        This method sends the :exc:`GeneratorExit` exception into the
        `coroutine`, which is expected to perform any necessary clean up and
        shutdown work and then terminate.

        .. note:: After this method is called, all subsequent calls to
            :meth:`send` **must** result in a :exc:`StopIteration` exception
            being raised.

        """


class INotLazy(interface.Interface):

    """Marker `interface` signalling that a `coroutine` is not `lazy`.

    A `coroutine` is called `lazy`, if it should only be executed when there
    are new incoming `messages` for it.  It is *not* `lazy` if the `coroutine`
    should be executed even when there are no incoming `messages` (i.e. for
    polling, etc.)

    :class:`INotLazy` `coroutines` will receive :obj:`None` objects as messages
    on their ``control`` `inbox` when there are no other `messages` to for
    them.

    .. note:: By default, all objects providing :class:`ICoroutine` are
        presumptively `lazy`.  They need to provide this `interface` to
        indicate otherwise.  This is more efficient and more natural for
        `coroutines`.  It also more accurately distinguishes them from regular
        `generators`.

    """


#---  Postoffices interfaces

class IPostOfficeFactory(interface.Interface):

    """`Interface` for `callables` that return :class:`IPostOffice` objects."""

    def __call__(link_ignores_duplicates=False, unlink_ignores_missing=False):
        """Return the desired `post office`.

        :param link_ignores_duplicates: If :obj:`True`, the
          :meth:`IPostOffice.register` method becomes `idempotent` and will not
          raise an exception when adding an already added `link`.
        :type link_ignores_duplicate: :class:`bool`
        :param unlink_ignores_missing: If :obj:`True`, the
          :meth:`*.unregister` method becomes `idempotent` and will not
          raise an exception when removing a `link` that was not already added.
        :type unlink_ignores_missing: :class:`bool`

        :returns: The desired `post office`.
        :rtype: :class:`IPostOffice`

        """


class IPostOffice(interface.Interface):

    """`Interface` that defines a `post office`.

    `Post offices` are objects that are responsible for delivering posted
    `messages` from `inboxes` to `outboxes`.  They are also responsible for
    keeping track of the `links` between `mailboxes`.

    That said, `message` posting and retrieval (and subsequent delivery to
    `coroutines`) is someone else's responsibility.  Usually it is the job of
    the `scheduler`.

    """

    def register(first_link, *other_links):
        """Register `links` between `coroutines`.

        When a `source` `coroutine`'s `outbox` is linked to a `sink`
        `coroutine`'s `inbox`, any `messages` posted from the `source`'s
        `outbox` will automatically be delivered to the message queue for the
        `sink`'s `inbox`, where it can be later retrieved for delivery to the
        `sink` `coroutine`.

        :param first_link: The first `link` to register.
        :type first_link: 4-:class:`tuple`
        :param other_links: Any other `links` to register.
        :type other_links: :class:`tuple` of 4-:class:`tuple`\s

        Each link should be a 4-:class:`tuple` in the form of :samp:`({source},
        {outbox}, {sink}, {inbox})`, where:

        :param source: The `source` `coroutine` to link.
        :type source: :class:`ICoroutine`
        :param outbox: The `source`'s `outbox` to link.
        :type outbox: :class:`unicode`
        :param sink: The `sink` `coroutine` to link.
        :type sink: :class:`ICoroutine`
        :param inbox: The `sink`'s `inbox` to link.
        :type sink_inbox: :class:`unicode`

        :raises m4us.core.exceptions.LinkExistsError: If a `source`'s `outbox`
          is already linked to a `sink`'s `inbox`, unless the `post office` was
          created with ``link_ignores_duplicates=True``.

        .. seealso:: The :class:`IPostOfficeFactory` `interface` for details on
            the ``link_ignores_duplicates`` parameter.

        """

    def unregister(first_link, *other_links):
        """Unregister previously registered `links`.

        This is the opposite of the :meth:`link` method.

        :param first_link: The first `link` to unregister.
        :type first_link: 4-:class:`tuple`
        :param other_links: Any other `links` to unregister.
        :type other_links: :class:`tuple` of 4-:class:`tuple`\s

        Each link should be a 4-:class:`tuple` in the same format as defined in
        the :meth:`link` method documentation.

        :raises m4us.core.exceptions.NoLinkError: If a `link` was not
          previously registered, unless the `post office` was created with
          ``unlink_ignores_missing=True``.

        .. note:: Unregistering one `link` should not affect any other links
            involving the `source` `outbox` or the `sink` `inbox`.

        .. note:: Any outstanding messages in the `sink`'s `inbox` message
            queue should still be kept for delivery.  The message queue should
            only be removed after all outstanding `messages` have been
            retrieved.

        .. seealso:: The :meth:`link` method for details on the format of a
            link.

        .. seealso:: The :class:`IPostOfficeFactory` `interface` for details on
            the ``unlink_ignores_missing`` parameter.

        """

    def post(source, outbox, message):
        """Post a `message` from the `source` `outbox`.

        When a `message` is posted, it is automatically sent to the message
        queues of all linked `sink` `inboxes` for later retrieval and delivery.

        :param source: The `source` `coroutine` that produced the `message`.
        :type source: :class:`ICoroutine`
        :param outbox: The `outbox` on which the `source` sent the `message`.
        :type outbox: :class:`unicode`
        :param message: The `message` that the `source` sent.
        :type message: :class:`object`

        :raises m4us.core.exceptions.NoLinkError: If the `source` `outbox` has
          not already been registered as a `source` in a `link`.

        """

    def retrieve(sink):
        """Retrieve all outstanding `messages` for a `sink` `coroutine`.

        As `messages` are posted, they are accumulated in message queues based
        on the registered `links`.  When this method is called, all the
        accumulated `messages` for the given `sink` `coroutine` are returned
        and the message queue for that `sink` is emptied.

        If there are no outstanding `messages` waiting in the message queue,
        then an empty iterable is returned.

        :param sink: The `sink` `coroutine` for which to retrieve `messages`.
        :type sink: :class:`ICoroutine`

        :returns: All outstanding `messages` in the form of :samp:`({inbox},
          {message})`.
        :rtype: iterable if 2-:class:`tuple`\s

        :raises m4us.core.exceptions.NotASinkError: If the given `coroutine` is
          not registered as a `sink` in any of the registered `links`.

        .. note:: It is the responsibility of the caller to make sure all the
            retrieved `messages` are delivered to the `sink` `coroutine`.

        """


#---  Schedulers interfaces

class ISchedulerFactory(interface.Interface):

    """`Interface` for `callables` that return :class:`IScheduler` objects."""

    def __call__(post_office, add_ignores_duplicates=False,
      remove_ignores_missing=False):
        """Return the desired `scheduler`.

        :param post_office: The `post office` through which to post and
          retrieve `messages`.
        :type post_office: :class:`IPostOffice`
        :param add_ignores_duplicates: If :obj:`True`, the
          :meth:`IScheduler.register` method becomes `idempotent` and will not
          raise an exception when adding an already added `coroutine`.
        :type add_ignores_duplicates: :class:`bool`
        :param remove_ignores_missing: If :obj:`True`, the
          :meth:`IScheduler.unregister` method becomes `idempotent` and will
          not raise an exception when removing a `coroutine` that was not
          already added.
        :type remove_ignores_missing: :class:`bool`

        :returns: The desired `scheduler`.
        :rtype: :class:`IScheduler`

        :raises exceptions.TypeError: If the given `post office` does not
          provide the :class:`IPostOffice` `interface`.

        """


class IScheduler(interface.Interface):

    """`Interface` that defines a `scheduler`.

    `Scheduler` objects are responsible for being the main program loop.  Their
    job is to run `coroutines`.  They are also responsible for retrieving and
    delivering `messages` from a `post office` to the `coroutines`, as well as
    posting back to the `post office` any `messages` emitted by the
    `coroutines`.

    """

    def register(first_coroutine, *other_coroutines):
        """Register one or more `coroutines` with the `scheduler`.

        In order for a `scheduler` to run a `coroutine`, it must first be added
        to (i.e. registered with) the `scheduler`.

        :param first_coroutine: The first `coroutine` to add.
        :type first_coroutine: :class:`ICoroutine`
        :param other_coroutines: Any other `coroutines` to add.
        :type other_coroutines: :class:`tuple` of :class:`ICoroutine`\s

        :raises exceptions.TypeError: If any given argument does not provide or
          cannot be adapted to :class:`ICoroutine`.
        :raises m4us.core.exceptions.DuplicateError: If any given `coroutine`
          has already been added, unless the `scheduler` was created with
          ``add_ignores_duplicates=True``.

        .. note:: `Schedulers` are not *required* to preserve or guarantee any
            particular order in which the `coroutines` will be run.  They may,
            however, *choose* to do so, if desired.

        .. seealso:: The :class:`ISchedulerFactory` `interface` for details on
            the ``add_ignores_duplicates`` parameter.

        """

    def unregister(first_coroutine, *other_coroutines):
        """Unregister one or more `coroutines` from the `scheduler`.

        This is the opposite of the :meth:`add` method.

        :param first_coroutine: The first `coroutine` to remove.
        :type first_coroutine: :class:`ICoroutine`
        :param other_coroutines: Any other `coroutines` to remove.
        :type other_coroutines: :class:`tuple` of :class:`ICoroutine`\s

        :raises m4us.core.exceptions.NotAddedError: If any given `coroutine` is
          not registered with the `scheduler`, unless the `scheduler` was
          created with ``remove_ignores_missing=True``.

        .. note:: This method should also call each `coroutine`'s
            :meth:`!close` method.

        .. seealso:: The :class:`ISchedulerFactory` `interface` for details on
            the ``remove_ignores_missing`` parameter.

        """

    def step():
        """Run one `coroutine`.

        This is the smallest unit of execution.  A single registered
        `coroutine` is run once for each `message` currently accumulated in
        its `post office` message queue.  Any resulting `messages` are also
        posted back to the `post office`.  This means that one call to this
        method can trigger repeated calls to the current `coroutine`, but only
        one `coroutine` should ever be executed.

        If a `coroutine` is `lazy`, it should only be executed when there are
        `messages` waiting to be delivered to it (or it is in the "shutting
        down" state, see below).  If it is *not* `lazy` (i.e. it provides the
        :class:`INotLazy` marker `interface`) and there are no `messages`
        waiting (as is the case with `producers`, for example), then a
        :obj:`None` object should be sent as the `message` to the `coroutine`
        on its ``control`` `inbox`.

        If a `coroutine` :keyword:`yield`\s only a :obj:`None` object (without
        even an `outbox`), the :obj:`None` should just be discarded.  This lets
        the `coroutine` indicate it has no `message` to send.

        If a `coroutine` :keyword:`yield`\s an :class:`IShutdown` `message`,
        that `message` should be posted to the `post office`, like a normal
        `message`, to allow the the `message` to cascade to other `coroutines`.
        Additionally, if the `coroutine` :keyword:`yield`\s an
        :class:`IShutdown` `message` on it's ``signal`` `outbox`, it should
        then be considered in a "shutting down" state.  Finally, if the
        :keyword:`yield`\ed :class:`IShutdown` cannot be posted to the `post
        office` (i.e. the `post office` raises an
        :class:`~m4us.core.exceptions.NoLinkError`), the the message should
        just be discarded.  This is so that `consumer`/`sink` `coroutines` can
        also emit :class:`IShutdown` messages to signal that they are shutting
        down.

        When in the "shutting down" state, no futher `post office` `messages`
        should be sent to the `coroutine`.  Instead, an :class:`IShutdown`
        `message` should be sent to it's ``control`` `inbox` every time this
        method is called, until the `coroutine` exits (i.e. raises
        :exc:`StopIteration`).  This allows `coroutines` to emit additional
        `messages` before shutting down and ensures that `lazy` `coroutines`
        always get enough `messages` to be able to shutdown properly.

        Finally, any `coroutine` that exits (i.e. raises :exc:`StopIteration`)
        should be removed from any run queues and have its
        :meth:`~m4us.core.interfaces.ICoroutine.close` method called.  After
        that no `messages` should ever be sent to it again.

        :raises m4us.core.exceptions.NeverRunError: If a `coroutine` is `lazy`
          but the `post office` says it is not configured to receive any
          `messages` (i.e. raises :exc:`~m4us.core.exceptions.NotASinkError`).
        :raises m4us.core.exceptions.NoLinkError: If the `post office` raises
          the exception and the message is not an :class:`IShutdown` `message`.
          :class:`IShutdown` `messages` are expected to be cascaded (even from
          `consumers`), so they do not cause the exception to be re-raised.

        .. note:: At least one `coroutine` is expected to be added before
            calling this method.  It is an error to do otherwise.

        .. seealso:: :class:`INotLazy` for details about the non-`lazy`
            `coroutines`.

        .. seealso:: :meth:`IPostOffice.post` for details on the
            :class:`~m4us.core.exceptions.NoLinkError` exception.

        """

    def cycle():
        """Cycle once through the main loop, running all eligible `coroutines`.

        `Schedulers` represent the main execution loop.  This method triggers
        a single cycle through that execution loop, calling the :meth:`step`
        method as many times as is appropriate.  Ideally all registered
        `coroutines` should have a chance to run.

        .. seealso:: The :meth:`step` method for details on how `coroutines`
            are run and on the exceptions that this method can raise as a
            result.

        """

    def run(cycles=None):
        """Start the `scheduler`, running all registered `coroutines`.

        This is the main execution loop.

        :param cycles: The number of cycles of the main loop to run through.
          One cycle is defined as a one call to the :meth:`cycle` method.  If
          :obj:`None` or not specified, then this method should run until all
          registered `coroutines` have shutdown (i.e. raised
          :exc:`StopIteration`).
        :type cycles: :class:`int` or :obj:`None`

        .. note:: If *cycles* is specified, it is expected that subsequent
            calls to this method should continue from where the last call left
            off.

        .. seealso:: The :meth:`cycle` method for details on what a single
            cycle entails and what exceptions may be raised as a result.

        """


#---  Containers interfaces

class IContainerFactory(interface.Interface):

    """`Interface` for `callables` that return :class:`IContainer` objects."""

    def __call__(*args, **kwargs):
        """Return the desired container.

        :param args: Any positional arguments that the `factory` may accept.
        :type args: :class:`tuple`
        :param kwargs: Any keyword arguments that the `factory` may accept.
        :type kwargs: :class:`dict`

        :returns: The desired container.
        :rtype: :class:`IContainer`

        :raises m4us.core.exceptions.InvalidLinkError: If any of the given or
          calculated `links` are invalid.

        """


class IContainer(interface.Interface):

    """`Interface` that defines a container.

    Containers are responsible for containing :class:`ICoroutine` objects and
    the `links` that connect them both to each other and to the container
    itself, if appropriate.

    All containers should calculate and provide :attr:`~IContainer.coroutines`
    and :attr:`~IContainer.links` attributes before they are used. The contents
    of :attr:`~IContainer.coroutines` should be able to be passed to the
    appropriate :meth:`IScheduler.register` method and the contents of
    :attr:`~IContainer.links` should be able to be passed to the appropriate
    :meth:`~IPostOffice.register` method.

    Additionally, containers can contain other :class:`IContainer` objects, in
    other words other containers.  In such a case,
    :attr:`~IContainer.coroutines` and :attr:`~IContainer.links` should include
    the `coroutines` and `links` from the sub-containers, excluding any
    duplicates from the other `coroutines` and `links` in the parent container.

    .. note:: Containers will usually provide :class:`ICoroutine` as well, but
        that is not strictly required by this interface.  The calculation and
        use of the above-mentioned two attributes makes it not a strict
        requirement.

    """

    coroutines = interface.Attribute(
        """All the contained `coroutines` to be added to the `scheduler`.

        The `coroutines` of any sub-containers should also be included for
        convenience.

        The contained `coroutines` can be added to the `scheduler` with code
        similar to :samp:`{scheduler}.add(*{container}.coroutines)`.

        :type: Immutable sequence of :class:`ICoroutine`\s

        .. seealso:: :meth:`IScheduler.register` for details about adding
            `coroutines` to `schedulers`.

        """)

    links = interface.Attribute(
        """All the `post office` `links` to be added to the `post office`.

        The `links` of any sub-containers should also be included for
        convenience.

        The `links` between the contained `coroutines` can be added to the
        `post office` with code similar to
        :samp:`{post_office}.register(*{container}.links)`.

        :type: Immutable sequence of 4-:class:`tuple`\s

        .. seealso:: :meth:`IPostOffice.register` for details about adding
            `links` to `post offices`.

        """)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
