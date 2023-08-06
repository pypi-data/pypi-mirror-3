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


"""Provides commonly used `messages` to be passed between `coroutines`."""


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
from m4us.core import interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class Message(object):

    """Base class for special `messages` passed between `coroutines`.

    :Implements: :class:`~m4us.core.interfaces.IMessage`
    :Provides: :class:`~m4us.core.interfaces.IMessageFactory`

    """

    ## pylint: disable=R0903

    interface.implements(interfaces.IMessage)
    interface.classProvides(interfaces.IMessageFactory)

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class Shutdown(Message):

    """`Message` that indicates that a `coroutine` should shutdown.

    :Implements: :class:`~m4us.core.interfaces.IShutdown`
    :Provides: :class:`~m4us.core.interfaces.IMessageFactory`

    """

    ## pylint: disable=R0903

    interface.implements(interfaces.IShutdown)
    interface.classProvides(interfaces.IMessageFactory)


class ProducerFinished(Message):

    """`Message` that indicates that a `producer` has finished.

    :Implements: :class:`~m4us.core.interfaces.IProducerFinished`
    :Provides: :class:`~m4us.core.interfaces.IMessageFactory`

    """

    ## pylint: disable=R0903

    interface.implements(interfaces.IProducerFinished)
    interface.classProvides(interfaces.IMessageFactory)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
