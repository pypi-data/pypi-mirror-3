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


"""Provides `backplanes` for `publisher`/`subscriber` interactions."""


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
from m4us.core import api as core
from m4us import interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

@core.coroutine()
@interface.implementer(interfaces.IBackplane)
@interface.provider(interfaces.IBackplaneFactory)
def backplane():
    """A `backplane` lets `publishers` send `messages` to `subscribers`.

    To create a `backplane`, just call this function and store the resulting
    `backplane` `coroutine`.  Then make the `backplane` available for import by
    any publishing and subscribing modules.

    To publish `messages` to the `backplane`, use the :func:`publish_to`
    function.

    To subscribe to a `backplane`, just `link` to the `backplane`'s ``outbox``
    and ``signal`` `outboxes` like any other `publisher` `coroutine`.

    :Implements: :class:`~m4us.interfaces.IBackplane`
    :Provides: :class:`~m4us.interfaces.IBackplaneFactory`

    .. seealso:: The :class:`~m4us.interfaces.IBackplane` interface for more
        details on `backplanes`.

    """
    publishers = set()
    inbox, message = (yield)
    while True:
        response = 'outbox', message
        if core.is_shutdown(inbox, message):
            if not publishers:
                yield 'signal', message
                break
            response = None
        elif inbox == 'control':
            response = 'signal', message
            registration = interfaces.IRegisterPublisher(message, None)
            if registration:
                publisher = registration.publisher
                if publisher in publishers:
                    ## pylint: disable=W0710
                    raise AlreadyRegisteredError(publisher=publisher)
                    ## pylint: enable=W0710
                publishers.add(publisher)
                response = None
            else:
                unregistration = interfaces.IUnregisterPublisher(message, None)
                if unregistration:
                    publisher = unregistration.publisher
                    try:
                        publishers.remove(publisher)
                    except KeyError:
                        ## pylint: disable=W0710
                        raise NotRegisteredError(publisher=publisher)
                        ## pylint: enable=W0710
                    response = None
        inbox, message = (yield response)


def publish_to(backplane_):
    """Return a `component` that can publish `messages` to the `backplane`.

    This is just a convenience function that returns a
    :class:`~m4us.core.containers.Pipeline` of a :class:`Publisher`
    `component`, the given :func:`backplane` object and a
    :func:`~m4us.core.coroutines.null_sink` `coroutine`.

    :param backplane: The `backplane` object to which to publish `messages`.
    :type backplane: :class:`~m4us.interfaces.IBackplane`

    :returns: A container `component` that will publish all sent `messages` to
      the given `backplane`.
    :rtype: :class:`~m4us.core.containers.Pipeline`

    .. note:: Since this function returns an
        :class:`~m4us.core.interfaces.IContainer` `component`, remember to
        register it's `coroutines` and `links` with the `scheduler` and `post
        office`, or include it in another container.

    """
    return core.Pipeline(Publisher(), backplane_, core.null_sink())


#---Classes--------------------------------------------------------------------

#---  Exceptions

class AlreadyRegisteredError(core.M4USException):

    """Raised when a `publisher` has attempted to register more than once.

    The default message requires a ``publisher`` attribute or keyword argument.

    .. seealso:: The :class:`~m4us.interfaces.IBackplane` `interface` for
        details about this exeption's usage.

    """

    _message = 'The publisher "{publisher!r}" was already registered.'


class NotRegisteredError(core.M4USException):

    """Raised when a `publisher` has not been registered by a `backplane`.

    The default message requires a ``publisher`` attribute or keyword argument.

    .. seealso:: The :class:`~m4us.interfaces.IBackplane` `interface` for
        details about this exeption's usage.

    """

    _message = 'The publisher "{publisher!r}" was not previsously registered.'


#---  Messages

class RegisterPublisher(core.Message):

    """`Message` for registering `publishers` with `backplanes`.

    :param publisher: The publishing object, specified as a keyword argument.
    :type publisher: :class:`object`

    :Implements: :class:`~m4us.interfaces.IRegisterPublisher`
    :Provides: :class:`~m4us.core.interfaces.IMessageFactory`

    .. seealso:: The :class:`Publisher` `component` and the
        :class:`~m4us.interfaces.IBackplane` `interface` for details about how
        this `message` is used.

    .. attribute:: publisher

        The `publisher` object to register.

        :type: *any*

    """

    ## pylint: disable=R0903

    interface.implements(interfaces.IRegisterPublisher)
    interface.classProvides(core.IMessageFactory)

    def __init__(self, **kwargs):
        """See class docstring for this method's documentation."""
        # Note: The publisher argument should always be spcified as a keyword
        #       argument in order to conform the to IMessageFactory interface.
        assert b'publisher' in kwargs, '"publisher" keyword argument required.'
        core.Message.__init__(self, **kwargs)


class UnregisterPublisher(RegisterPublisher):

    """`Message` for unregistering `publishers` with `backplanes`.

    :param publisher: The publishing object, specified as a keyword argument.
    :type publisher: :class:`object`

    :Implements: :class:`~m4us.interfaces.IUnregisterPublisher`
    :Provides: :class:`~m4us.core.interfaces.IMessageFactory`

    .. seealso:: The :class:`Publisher` `component` and the
        :class:`~m4us.interfaces.IBackplane` `interface` for details about
        how this `message` is used.

    .. attribute:: publisher

        The `publisher` object to unregister.

        :type: *any*

    """

    ## pylint: disable=R0903

    interface.implementsOnly(interfaces.IUnregisterPublisher)
    interface.classProvides(core.IMessageFactory)


#---  Components

class Publisher(core.Component):

    """`Component` that registers with a `backplane` before sending `messages`.

    :class:`~m4us.interfaces.IBackplane` `coroutines` expect that registration
    and un-registration `messages` will be sent by `publishers` before and
    after usage.  This `component` handles those actions transparently.  Just
    link this `component`'s ``outbox`` and ``signal`` `outboxes` to the
    `backplane`'s ``inbox`` and ``control`` `inboxes`.

    This is usually all handled automatically by the :func:`publish_to`
    function.

    `Messages` sent to this class will be forwarded back out, but only after an
    :class:`~m4us.interfaces.IRegisterPublisher` `message` is emitted first.
    Similarily, before an :class:`~m4us.core.interfaces.IShutdown` `message` is
    forwarded on, an :class:`~m4us.interfaces.IUnregisterPublisher` `message`
    is emitted first.

    :Implements: :class:`~m4us.core.interfaces.ICoroutine` and
      :class:`~m4us.core.interfaces.INotLazy`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    .. seealso:: The :func:`publish_to` function for the normal way to publish
        to a `backplane`.

    .. seealso:: The :class:`RegisterPublisher` and
        :class:`UnregisterPublisher` classes as examples of concrete classes
        that `publishers` can use for registration and unregistration.

    """

    ## pylint: disable=R0903

    # This is needed so that all shutdown messages are emitted after the
    # IShutdown is sent in.
    interface.implements(core.INotLazy)
    interface.classProvides(core.ICoroutineFactory)

    def _main(self):
        """Publish `messages` to a `backplane`.

        .. seealso:: This class' docstring and the
            :meth:`~m4us.core.interfaces.IComponent._main` method for details
            about this method.

        """
        current_inbox, current_message = (yield)
        # The use of self here is why this is a component and not just a
        # coroutine.
        response = 'signal', RegisterPublisher(publisher=self)
        while True:
            next_inbox, next_message = (yield response)
            if current_inbox == 'control' and current_message is None:
                response = None
            elif core.is_shutdown(current_inbox, current_message):
                yield 'signal', UnregisterPublisher(publisher=self)
                yield 'signal', current_message
                break
            else:
                response = 'outbox', current_message
            current_inbox, current_message = next_inbox, next_message


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
