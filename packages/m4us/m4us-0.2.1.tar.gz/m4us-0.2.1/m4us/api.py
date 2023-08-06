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


"""Provides convenient access to all public objects.

This module imports all public objects from all the other modules in order to
provide convenient access to them.  This way you can use the following import
line in your code::

  import m4us.api as m4us

By providing this convenience in a separate module (:mod:`m4us.api`), instead
of in the package root (:mod:`m4us`), projects working under tight memory
constraints can reduce the memory footprint of this project by instead directly
importing only those modules they need.

.. seealso:: :doc:`/api/index` and the various module documentation for details
    on the available objects in imported into this module.

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

#---  Project imports
from m4us.core import utils

## pylint: disable=W0401
from m4us.core.api import *
## pylint: enable=W0401
## pylint: disable=W0611
from m4us.interfaces import (
  IThreadedCoroutine,
  IBackplaneFactory,
  IBackplane,
  IRegisterPublisher,
  IUnregisterPublisher,
)
from m4us.concurrency import (
  ThreadedCoroutine,
)
from m4us.backplanes import (
  backplane,
  publish_to,
  NotRegisteredError,
  AlreadyRegisteredError,
  RegisterPublisher,
  UnregisterPublisher,
  Publisher,
)
## pylint: enable=W0611

#---Globals--------------------------------------------------------------------

__all__ = []


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------

## pylint: disable=W0212
__all__.extend(utils._public_object_names(globals()))
## pylint: enable=W0212

#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
