# -*- coding: utf-8 -*-

#---Header---------------------------------------------------------------------

# This file is part of Message For You Sir (m4us).
# Copyright © 2009-2012 Krys Lawrence
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
from future_builtins import ascii, filter, hex, map, oct, zip  ## NOQA
## pylint: enable=W0622, W0611

#---  Third-party imports
## pylint: disable=F0401
from zope import interface
## pylint: enable=F0401

#---  Project imports
from m4us.core import interfaces


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

@interface.implementer(interfaces.IMessage)
@interface.provider(interfaces.IMessageFactory)
class Message(object):

    """Base class for special `messages` passed between `coroutines`.

    :implements: :class:`m4us.core.interfaces.IMessage`
    :provides: :class:`m4us.core.interfaces.IMessageFactory`

    """

    ## pylint: disable=R0903

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


## pylint: disable=R0903
@interface.implementer(interfaces.IShutdown)
@interface.provider(interfaces.IMessageFactory)
class Shutdown(Message):

    """`Message` that indicates that a `coroutine` should shutdown.

    :implements: :class:`m4us.core.interfaces.IShutdown`
    :provides: :class:`m4us.core.interfaces.IMessageFactory`

    """
## pylint: enable=R0903


## pylint: disable=R0903
@interface.implementer(interfaces.IProducerFinished)
@interface.provider(interfaces.IMessageFactory)
class ProducerFinished(Message):

    """`Message` that indicates that a `producer` has finished.

    :implements: :class:`m4us.core.interfaces.IProducerFinished`
    :provides: :class:`m4us.core.interfaces.IMessageFactory`

    """
## pylint: enable=R0903


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
