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


"""Provides common utilities for the rest of the project."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import types
import weakref

#---  Third-party imports
import decorator

#---  Project imports
from m4us.core import interfaces


#---Globals--------------------------------------------------------------------

## pylint: disable=W0105
_DEFAULT_NAME_EXCLUDES = ('filter', 'map', 'zip')
"""The default object names to always exclude from :func:`_is_private_object`.

This global is here so that other modules can use it as a base when needing to
include additional names.

It currently only includes the names of objects in the *future_builtins* module
that do not originate in that module (and so their *__module__* module
attribute is not set to ``future_builtins``.  E.g. ``'filter'``, ``'map'``,
etc.

"""
## pylint: enable=W0105


#---Functions------------------------------------------------------------------

def _is_private_object(object_name, object_, excludes=_DEFAULT_NAME_EXCLUDES):
    """Return :obj:`True` if the object is private.

    Private object means any object that would not be considered part of a
    public API.  Specifically, an object is considered private if:

      * Its name is in the excludes list, or
      * Its name starts with an underscore ("_"), or
      * It is a module, or
      * It is from the *__future__* or *future_builtins* modules.

    :param object_name: The name of the object to check.
    :type object_name: :class:`str` or :class:`unicode`
    :param object_: The object to check.
    :type object_: :class:`object`
    :param excludes: A sequence of object names to always consider as private.
      The default just includes the names from *future_builtins* that original
      elsewhere.
    :type excludes: *sequence* of :class:`str` or :class:`unicode`

    :returns: :obj:`True` if the object is considered non-public, :obj:`False`
      otherwise.
    :rtype: :class:`bool`

    """
    return (
      object_name in excludes or
      object_name.startswith('_') or
      isinstance(object_, types.ModuleType) or
      (hasattr(object_, '__module__') and object_.__module__ in ('__future__',
        'future_builtins')))


def _public_object_names(namespace, excludes=_DEFAULT_NAME_EXCLUDES):
    """`Generator` of public names in a namespace.

    Given a namespace (like the *__dict__* of a module, for example), this
    `generator` will yield the names of all public objects in the namespace.

    Public object is defined as whenever :func:`_is_private_object` returns
    :obj:`False`.

    Example usage:

    >>> import somemodule
    >>> for name in _public_object_names(vars(somemodule)):
    >>>     print(name)

    :param namespace: The namesapce in which to search for objects.
    :type namespace: :class:`dict`
    :param excludes: A sequence of object names to always exclude.
    :type excludes: *sequence* of :class:`str` or :class:`unicode`

    :returns: An iterator of public object names from the given namespace.
    :rtype: :class:`~types.GeneratorType`

    """
    excludes = set(excludes)
    for name, object_ in namespace.items():
        if _is_private_object(name, object_, excludes):
            continue
        yield name


def easy_link(first_coroutine, second_coroutine, *other_coroutines):
    """Return `links` connecting the `coroutines` in the standard way.

    The given `coroutines` are linked in a `pipeline` (not to be confused with
    a :class:`~m4us.core.containers.Pipeline`) of ``outbox`` to ``inbox`` and
    ``signal`` to ``control`` `mailboxes`.  The first `coroutine` will only
    have it's ``outbox`` and ``signal`` `mailboxes` linked and the last
    `coroutine` will only have it's ``inbox`` and ``control`` `mailboxes`
    linked.  `Coroutines` in the middle will be linked to the previous and next
    `coroutines` in order.

    The resulting `links` can then be passed to a `post office`.

    :param first_coroutine: A minimum of two `coroutines` are required. This is
      the first one.
    :type first_coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param second_coroutine: The second `coroutine`.
    :type second_coroutine: :class:`~m4us.core.interfaces.ICoroutine`
    :param other_coroutines: Any other `coroutines` to `link` after the second
      one.
    :type other_coroutines: :class:`tuple` of
      :class:`~m4us.core.interfaces.ICoroutine`

    :returns: A set of `mailbox` `links` to be given to a `post office`.
    :rtype: :class:`set` of 4-:class:`tuple`\s

    .. note:: Normally one would just use the
        :class:`~m4us.core.containers.Pipeline` class, but this provides just
        the `links`, which could be useful to other `container` classes.

    .. seealso:: The :class:`~m4us.core.interfaces.IPostOffice` `interface` for
        more information on `links`, `mailboxes` and `post offices`.

    .. seealso:: The :class:`~m4us.core.containers.Pipeline` class for the
        normal way to construct `coroutine` `pipelines`.

    """
    sources = (first_coroutine, second_coroutine) + other_coroutines[:-1]
    sinks = (second_coroutine,) + other_coroutines
    links = set()
    for source, sink in zip(sources, sinks):
        links.update((
          (source, 'outbox', sink, 'inbox'),
          (source, 'signal', sink, 'control'),
        ))
    return links


def is_shutdown(inbox, message, expected_inbox='control'):
    """Return :obj:`True` if the given `message` signals a shutdown.

    `Coroutines` are expected to shutdown when they receive a shutdown
    `message`.  This is a convenience function that returns :obj:`True` if
    `inbox` is ``control`` (by default) and the `message` object provides or is
    adaptable to :class:`~m4us.interfaces.IShutdown`.

    :param inbox: The `inbox` in which with `message` was received.
    :type inbox: :class:`unicode`
    :param message: The `message` object that was received.
    :type message: any
    :param expected_inbox: The `inbox` in which
      :class:`~m4us.interfaces.IShutdown` `messages` are expected.  This
      parameter lets the default be overridden.
    :type expected_inbox: :class:`unicode`

    :returns: :obj:`True` if the `message` signals that the `coroutine` should
      shutdown, :obj:`False` otherwise.
    :rtype: :class:`bool`

    """
    return inbox == expected_inbox and interfaces.IShutdown(message, False)


def _strip_first_parameter(function_maker):
    """Strip the first parameter from a function signature.

    This function ajusts a :class:`decorator.FunctionMaker` instance, removing
    the first parameter, along with it's default value if it has one.  It
    does not remove any :samp:`*{args}` or :samp:`**{kwargs}` parameters,
    however, even if they are the first parameter.  If there are no positional
    parameters, no adjustments are made.

    This function is meant to make constructing certain signature-altering
    decorators easier to build.

    :parameter function_maker: The :class:`~decorator.FunctionMaker` instance
      to alter.
    :type function_maker: :class:`decorator.FunctionMaker`

    """
    if not function_maker.args and not function_maker.varargs:
        # E.g. def func():
        # E.g. def func(**kwargs):
        return
    if len(function_maker.args) == 1 and not function_maker.varargs and not \
      function_maker.varkw:
        # E.g. def func(first):
        function_maker.signature = ''
        function_maker.args = []
    elif not function_maker.args and function_maker.varargs:
        # E.g. def func(*args):
        # Leave signature untouched.
        pass
    else:
        # E.g. def func(first, second):
        # E.g. def func(first, *args):
        # E.g. def func(first, **kwargs):
        # Remove first argument.
        function_maker.signature = function_maker.signature.split(', ', 1)[1]
        function_maker.args.pop(0)
    if function_maker.defaults and len(function_maker.defaults) > len(
      function_maker.args):
        # E.g. def func(first='default'):
        # E.g. def func(first='default', other='other default'):
        function_maker.defaults = function_maker.defaults[1:]
        if not function_maker.defaults:
            function_maker.defaults = None


def _function_wrapper_from_template(function, template,
  strip_first_parameter=False, **kwargs):
    """Construct and return a wrapper function from a template string.

    This function can create a function wrapper from a template, preserving the
    signature of the original function, if desired.  It's main purpose is to
    be used in decorators to create function wrappers with preserved or
    modified signatures, names and doctstrings.

    The template is typically in the form of::

      def %(name)s(%(signature)s):
          # Do something
          return _func_(%(signature)s)
          # Do something else

    where ``%(name)s`` is replaced the with name of the given function,
    ``%(signature)s`` is replaced with the function's signature and ``_func_``
    is a reference to the given function.  These variables are not required,
    however.

    If *strip_first_parameter* is :obj:`True`, then ``%(signature)s`` is
    modified to remove the first parameter (excluding :samp:`*{args}` and
    :samp:`**{kwargs}`).  This is useful if the wrapper will pass in the first
    argument, but the rest of the given function's signature should be passed
    in through the wrapper.

    Also, any additional keyword arguments that are passed to this function
    will become global variables in the wrapper's namespace.  This is useful
    for passing in additional dependencies to the wrapper function.

    :parameter function: The function to wrap and on which to base the
      wrapper's signature, name and docstring.
    :type function: :obj:`~types.FunctionType`
    :parameter template: The template for the wrapper function.
    :type template: :obj:`str` or :obj:`unicode`
    :parameter strip_first_parameter: If :obj:`True`, the first parameter of
      the given function's signature will be stripped off of the
      ``%(signature)s`` variable used in the template.  Default is
      :obj:`False`.
    :type strip_first_parameter: :obj:`bool`

    :returns: A wrapper function created from the given template.
    :rtype: :obj:`~types.FunctionType`

    :raises TypeError: If the first argument is not a function.
    :raises ValueError: If *strip_first_parameter* is :obj:`True` and the given
      function does not accept at least one parameter.
    :raises SyntaxError: If the template is not valid.

    :see also: :class:`decorator.FunctionMaker` for additional details on
      templates and available variables.

    """
    # Note: All this messing around with FunctionMaker is in order to preserve
    # the function signature in the filter coroutine factory function, possibly
    # minus the first positional argument, which is the inbox message delivered
    # to the coroutine.
    if not isinstance(function, types.FunctionType):
        # No support for being a class decorator yet.
        raise TypeError('First argument must be a function.')
    wrapper_maker = decorator.FunctionMaker(function)
    if strip_first_parameter:
        ## pylint: disable=E1101
        if not wrapper_maker.args and not wrapper_maker.varargs:
            ## pylint: enable=E1101
            # E.g. def func():
            # E.g. def func(**kwargs):
            raise ValueError('Function must accept at least one positional '
              'argument if strip_first_parameter=True.')
        _strip_first_parameter(wrapper_maker)
    eval_dictionary = function.__globals__.copy()
    eval_dictionary['_func_'] = function
    eval_dictionary.update(kwargs)
    wrapper = wrapper_maker.make(template, eval_dictionary,
      undecorated=function)
    return wrapper


#---Classes--------------------------------------------------------------------

## pylint: disable=R0903
class _ObjectStandIn(object):

    """Instances of this class are stand-ins for other objects.

    This class is used by the :class:`_ObjectStandInRegistry`. Stand-ins can be
    used, for example, to hold attributes when for other objects that cannot
    (i.e. :class:`~types.GeneratorType`) or in any other situation where using
    the original object is not suitable.

    .. seealso:: :class:`_ObjectStandInRegistry` for details on how to work
        with stand-ins.

    """

## pylint: enable=R0903


class _ObjectStandInRegistry(object):

    """Provides a registry for object stand-ins.

    Objects can be registered and given stand-in objects to use in their place.
    Those same stand-ins can then be retrieved at a later time and used again.

    Stand-ins can be used in any situation where the original object cannot or
    should not be used directly.  The prime use case is when adding additional
    attributes to an object that cannot accept additional objects.

    Original objects are only stored as weak references so there should not be
    any memory leaks from registering.

    When an object is registered, an instance of :class:`_ObjectStandIn` is
    returned.  That stand-in instance can then subsequently be retrieved using
    either the :meth:`get_stand_in` method or by mapping lookup.  For example::

      stand_in = registry[original_object]

    An object can be unregistered either by using the :meth:`unregister` method
    or by using the :keyword:`del` keyword in the mapping lookup.  For
    example::

      del registry[original_object]

    """

    def __init__(self):
        """See class docstring for this method's documentation."""
        self._stand_ins = weakref.WeakKeyDictionary()

    def __getitem__(self, object_):
        """See class docstring for this method's documentation."""
        return self._stand_ins[object_]

    def __delitem__(self, object_):
        """See class docstring for this method's documentation."""
        if object_ in self._stand_ins:
            del self._stand_ins[object_]

    def register(self, object_):
        """Register an object as having a stand-in and return the stand-in.

        This method registers and created the stand-in object.  Registering the
        same object again will return the same stand-in.

        :param object_: The object to register.
        :type object_: *any*

        :returns: A stand-in object.
        :rtype: :class:`_ObjectStandIn`

        """
        return self._stand_ins.setdefault(object_, _ObjectStandIn())

    def is_registered(self, object_):
        """Return :obj:`True` if the object is registered in the registry.

        :param object_: The object to check.
        :type object_: *any*

        :returns: :obj:`True` if the object is registered, :obj:`False`
          otherwise.
        :rtype: :class:`bool`

        """
        return object_ in self._stand_ins

    def clear(self):
        """Clear the registry of all registrations.

        This will cause the stand-ins to be garbage collected if no other
        references to them are held.

        """
        self._stand_ins.clear()

    def unregister(self, object_):
        """Remove an object from the registry

        This method unregisters an object.  This will cause the stand-in to be
        garbage collected if no other references to it are held.  Unregistering
        an object  that is already not registered will do nothing.

        :param object_: The registered object to remove.
        :type object_: *any*

        """
        del self[object_]

    def get_stand_in(self, object_):
        """Teturn the stand-in for the given object.

        :param object_: The registered object to get.
        :type object_: *any*

        :returns: The object's stand-in.
        :rtype: :class:`_ObjectStandIn`

        :raises ValueError: If the object is not registered.

        """
        try:
            return self[object_]
        except KeyError:
            raise ValueError('{0} not found.'.format(repr(object_)))


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
