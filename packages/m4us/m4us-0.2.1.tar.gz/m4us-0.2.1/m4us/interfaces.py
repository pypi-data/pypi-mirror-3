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


"""Provides the `interface` definitions for all important non-core objects."""

## pylint: disable=W0232


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


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Concurrency interfaces

class IThreadedCoroutine(core.ICoroutine):

    """`Interface` that defines threaded `coroutines`.

    Threaded `coroutines` work just like regular `coroutines`, except they run
    in separate threads.  This `interface` provides an additional method for
    explicitly starting the thread when it is appropriate.

    The advantage of running a threaded `coroutine` is that it's methods should
    return immediately allowing the main thread to continue running without
    blocking.

    The consequence of this, however, is that a `message` received from the
    `coroutine` is not necessarily the immediate response to the `message` that
    was sent in.  That is, both sent and received `messages` are queued up in
    order and potentially processed at different rates.  This is also true for
    thrown exceptions.

    """

    ## pylint: disable=E0211
    def start():
        """Start the `coroutine` thread.

        :raises RuntimeError: If the thread is already running.

        """
    ## pylint: enable=E0211


#---  Backplanes interfaces

class IBackplaneFactory(core.ICoroutineFactory):

    """`Interface` for `callables` that return :class:`IBackplane` objects."""

    ## pylint: disable=R0903

    ## pylint: disable=E0211
    def __call__(*args, **kwargs):
        """Return the desired `backplane`.

        :param args: Any arguments to pass to the `factory` `callable`.
        :type args: :class:`tuple`
        :param kwargs: Keywords arguments to pass to the `factory` `callable`.
        :type kwargs: :class:`dict`

        :returns: The desired `backplane` `coroutine`
        :rtype: :class:`IBackplane`

        """
    ## pylint: enable=E0211


## pylint: disable=R0903
class IBackplane(core.ICoroutine):

    """`Interface` that defines `backplane` `coroutines`.

    This is an analogue to Kamaelia_'s :class:`!Backplane`, and
    :class:`!SubscribeTo` components.

    A `backplane` is a `coroutine` to which one or more `publishers` can send
    `messages`, and to which one or more `subscribers` can then recieve those
    `messages`.  The advantage of using a `backplane` is that the `subscribers`
    do not need to know about the `publishers` and vice versa.  The only thing
    they each need to have is the `backplane` `coroutine` through which they
    are communicating.

    `Publishers` register themselves by sending an :class:`IRegisterPublisher`
    `message` to the `backplane`'s ``control`` `inbox`.  Similarily, they
    unregister themselves by sending an :class:`IUnregisterPublisher`
    `message`.  `Publishers` are expected to register before sending any
    `messages` and unregister before sending any
    :class:`~m4us.core.interfaces.IShutdown` `messages`.  All this is needed so
    that the backplane knows when the last `publisher` is done and can wait
    until then to shutdown.

    `Subscribers` to a `backplane`, just need `link` to the `backplane`'s
    ``outbox`` and ``signal`` `outboxes` like any other `producer` `coroutine`.

    A `backplane` will shutdown upon reciept of an
    :class:`~m4us.core.interfaces.IShutdown` `message` on it's ``control``
    `inbox`, but only when there are no registered `publishers` (i.e. they have
    all unregistered as part of their shutdown).  It will also forward the
    shutdown `message` on to all `subscribers` on it's ``signal`` `outbox`,
    but again, only when there are no registered `publishers`.

    :raises m4us.backplanes.NotRegisteredError: If a `publisher` attempts to
      unregister itself without already being registered.
    :raises m4us.backplanes.AlreadyRegisteredError: If a `publisher` attempts
      to register itself more than once.

    .. _Kamaelia: http://www.kamaelia.org/

    """
## pylint: enable=R0903


class IRegisterPublisher(core.IMessage):

    """`Interface` for `messages` that register `publishers` with `backplanes`.

    :param publisher: `Messages` providing this `interface` should require a
      publishing object, specified as a keyword argument.
    :type publisher: :class:`object`

    .. seealso:: The :class:`IBackplane` `interface` for details about
        `messages` that use this `interface`.

    """

    ## pylint: disable=R0903

    publisher = interface.Attribute(
        """The `publisher` object to register.

        :type: :class:`object`

        """)


class IUnregisterPublisher(core.IMessage):

    """`Interface` for `messages` that un-register `backplane` `publishers`.

    :param publisher: `Messages` providing this `interface` should require a
      publishing object, specified as a keyword argument.
    :type publisher: :class:`object`

    .. seealso:: The :class:`IBackplane` `interface` for details about
        `messages` that use this `interface`.

    """

    ## pylint: disable=R0903

    publisher = interface.Attribute(
        """The `publisher` object to un-register.

        :type: :class:`object`

        """)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
