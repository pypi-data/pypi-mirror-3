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


"""Provides all the custom exceptions for the project core."""


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


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class M4USException(Exception):

    """Base class for all exceptions in this project.

    Despite Python_'s deprecation_ of the *message* attribute, sub-classes of
    this exception can (and should) set the :attr:`_message` attribute to be a
    default message or message template (see below).  The message can also be
    overridden by the first positional argument.

    Additionally, any keyword arguments given at instantiation will become
    attributes of the instance.  This allows for additional context to be
    provided when appropriate.

    Finally, it is expected that only the Unicode representation of the
    exception will be used.  That representation will substitute any fields in
    the form of ``{field}`` with instance or class attributes.

    :param message: Optional overridden message or message template to use.
    :type message: :class:`unicode`
    :param kwargs: Any keyword arguments to convert to instance attributes.
    :type kwargs: :class:`dict`

    .. seealso:: Python_'s new `string formatting method`_ for details on
        string templates.

    .. _Python: http://python.org
    .. _deprecation: http://www.python.org/dev/peps/pep-0352/#retracted-ideas
    .. _`string formatting method`:
        http://docs.python.org/library/string.html#format-string-syntax

    .. autoattribute:: _message

    """

    ## pylint: disable=W0105
    _message = 'An exception occurred in the m4us package.'
    """Default message or message template for the exception.

    :type: :class:`unicode`

    .. note:: This should be overridden by sub-classes.

    """
    ## pylint: enable=W0105

    def __init__(self, message=None, **kwargs):
        """See class docstring for this method's documentation."""
        Exception.__init__(self)
        if message is not None:
            self._message = message
        self.__dict__.update(kwargs)

    def __str__(self):
        """See class docstring for this method's documentation."""
        return self._message.format(**self.__dict__)


#---  Postoffices exceptions

class LinkExistsError(M4USException):

    """Raised when a `link` already exists in a `post office`.

    The default exception message requires a ``link`` attribute or keyword
    argument.

    """

    _message = 'The link "{link!r}" has already been established.'


class NoLinkError(M4USException):

    """Raised when a particular `link` has not already been established.

    The default exception message requires ``source_outbox`` and ``sink_inbox``
    attributes or keyword arguments.

    """

    _message = ('The source/outbox "{source_outbox!r}" or the sink/inbox '
      '"{sink_inbox!r}" has not been linked.')


class NotASinkError(M4USException):

    """Raised when a `coroutine` is not configured to receive `messages`.

    The default exception message requires a ``coroutine`` attribute or keyword
    argument.

    """

    _message = ('The coroutine "{coroutine!r} is not linked to receive '
      'messages.')


#---  Schedulers exceptions

class DuplicateError(M4USException):

    """Raised when attempting to register an already registered `coroutine`.

    The default exception message requires a ``coroutine`` attribute or keyword
    argument.

    """

    _message = 'Coroutine "{coroutine!r}" has already been added.'


class NotAddedError(M4USException):

    """Raised when attempting to unregister an unknown `coroutine`.

    The default exception message requires a ``coroutine`` attribute or keyword
    argument.

    """

    _message = 'Coroutine "{coroutine!r}" was not previously added.'


class NeverRunError(M4USException):

    """Raised if a `lazy` `coroutine` will never receive any `messages`.

    The default exception message requires a ``coroutine`` attribute or keyword
    argument.

    """

    _message = ('Coroutine "{coroutine!r}" will never be run because it '
      'receives no messages and is lazy.')


#---  Containers exceptions

class InvalidLinkError(M4USException):

    """Raised when a `link` between a container and it's child is invalid.

    The default exception message requires ``source_outbox`` and ``sink_inbox``
    attributes or keyword arguments.

    """

    _message = ('The link "{source_outbox!r}" to "{sink_inbox!r}" is not '
      'valid.  Children can only have pass-through links to their parent.')


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
