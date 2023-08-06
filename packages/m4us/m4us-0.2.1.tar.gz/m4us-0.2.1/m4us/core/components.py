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


"""Provides various kinds of `Component` classes.

`Components` are `coroutines` with context.  That is, they are classes that
implement :class:`~m4us.core.interfaces.ICoroutine`, but can also store and
access instance attributes.

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
# This is imported directly for the sample coroutine
## pylint: disable=F0401
from zope.interface import classProvides
## pylint: enable=E0611, F0401

#---  Project imports
from m4us.core import interfaces
# These are imported directly for the sample coroutine
from m4us.core.utils import is_shutdown
from m4us.core.interfaces import ICoroutineFactory


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class Component(object):

    """Base class for `components`.

    `Components` act like `coroutines` but can store and retrieve context via
    instance attributes.  This corresponds in concept to Kamaelia_'s
    :class:`!Component` class.

    `Components` have an internal `coroutine` defined in the :meth:`_main`
    method, which sub-classes should implement.

    :param kwargs: Any keyword arguments given at instantiation are
      automatically set as instance attributes for convenience.
    :type kwargs: :class:`dict`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    .. _Kamaelia: http://www.kamaelia.org/

    .. automethod:: _main

    """

    interface.implements(interfaces.ICoroutine)
    interface.classProvides(interfaces.ICoroutineFactory)

    def __init__(self, **kwargs):
        """See class docstring for this method's documentation."""
        self.__dict__.update(kwargs)
        self._coroutine = self._main()
        self._coroutine.send(None)

    def _main(self):
        """The `component`'s `coroutine`.

        Sub-classes are expected to override this method.  It should be a
        `coroutine` which will automatically be activated upon instantiation.

        This `coroutine` should work just like regular `coroutines`, but has
        access to ``self`` and any context that the instance contains.

        """
        raise NotImplementedError(
          'Sub-classes must implement the _main() method.')

    def send(self, message):
        """Send the `message` to the `component`.

        This method just passes the `message` on to the internal `coroutine`
        defined in :meth:`_main`, returning any resulting `message`.

        .. seealso:: The :class:`~m4us.core.interfaces.ICoroutine` `interface`
            for details about this method.

        """
        return self._coroutine.send(message)

    def throw(self, exception):
        """Send the exception to the `component`.

        This method just passes the exception on to the internal `coroutine`
        defined in :meth:`_main`, returning any resulting `message` or raising
        the uncaught exception.

        .. seealso:: The :class:`~m4us.core.interfaces.ICoroutine` `interface`
            for details about this method.

        """
        return self._coroutine.throw(exception)

    def close(self):
        """Terminate the `component`.

        This method just calls :meth:`!close` on the `component`'s internal
        `coroutine` defined in :meth:`_main`.

        .. seealso:: The :class:`~m4us.core.interfaces.ICoroutine` `interface`
            for details about this method.

        """
        self._coroutine.close()


# [[start SampleComponent]]
class SampleComponent(Component):

    """Component that passes all messages through."""

    classProvides(ICoroutineFactory)

    def _main(self):
        """Pass all messages through."""
        inbox, message = (yield)
        while True:
            if is_shutdown(inbox, message):
                yield 'signal', message
                break
            ## Your code goes here.
            inbox, message = (yield 'outbox', message)

    # [[end SampleComponent]]

    # The docstring for SampleComponent is set like this so that it can include
    # it's own source code in the docs.  The literalinclude directive won't
    # work completely correctly if the docstring is inline.  Also note that
    # class docstrings cannot be changed after the class definition is
    # complete.
    __doc__ = """`Component` that passes all `messages` through.

    This `component` is meant to provide a canonical example of what a
    `component` used with this project looks like.

    Like :func:`~m4us.core.coroutines.sample_coroutine`, any `messages` sent to
    it on any `inbox` will be sent back out on it's ``outbox`` `outbox`.  It is
    also well behaved in that it will shutdown on any
    :class:`~m4us.core.interfaces.IShutdown` `message`, forwarding it on before
    quitting.

    The full code for this `component` is:

    .. literalinclude:: ../../../../m4us/core/components.py
        :linenos:
        :start-after: # [[start SampleComponent]]
        :end-before: # [[end SampleComponent]]

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    .. seealso:: The :func:`~m4us.core.coroutines.sample_coroutine` `coroutine`
        for details on why the :meth:`_main` method is written the way it is.

    """


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
