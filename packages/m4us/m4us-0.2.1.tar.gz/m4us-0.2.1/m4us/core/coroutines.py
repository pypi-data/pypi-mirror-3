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


"""Provides support for using regular Python_ `coroutines`.

.. _Python: http://python.org

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

import types

#---  Third-party imports
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611
import decorator

#---  Project imports
from m4us.core import utils, interfaces, messages
# This is imported directly for the sample coroutine
from m4us.core.utils import is_shutdown


#---Globals--------------------------------------------------------------------

## pylint: disable=C0103
_coroutine_stand_in_registry = None
## pylint: enable=C0103

_COROUTINE_FACTORY_TEMPLATE = """\
def %(name)s(%(signature)s):
    from {module_path} import {factory_name} as factory
    return factory(_func_, %(signature)s)
"""


#---Functions------------------------------------------------------------------

def _interface_adapter_hook(interface_, coroutine_, registry=None):
    """`Adapter` to adapt Python_ `coroutines` to their provided `interfaces`.

    `Components`, classes and regular functions can (and are expected to) just
    declare provided interfaces directly.  They do not need this adapter.

    Python_ `coroutines`, on the other hand, are really instances of
    :class:`~types.GeneratorType`.  They cannot be made to directly declare
    proivided interfaces because one cannot add additional attributes to the
    `generator` object.  That is where this `adapter` comes in.

    This `adapter` just checks to see if the `coroutine` has a registered
    stand-in object in the registry and that the stand-in provides the given
    `interface`.  If it does, the `coroutine` is returned unchanged.
    Otherwise, :obj:`None` is returned, which signals that adaptation was not
    possible.

    Since the :func:`coroutine` decorator automatically registers interfaces
    implemented by the `coroutine`'s `factory` function as those provided by
    the `coroutine` itself, adaptation to the given `interface` happens
    transparently.

    :param interface_: The `interface` that must be provided.
    :type interface_: :class:`~zope.interface.Interface`
    :param coroutine_: The `coroutine` to verify.
    :type coroutine_: :class:`~m4us.core.interfaces.ICoroutine`

    :returns: The given `coroutine` if it provides the `interface` or
      :obj:`None` otherwise.
    :rtype: :class:`~m4us.core.interfaces.ICoroutine` or :obj:`None`

    """
    if registry is None:
        registry = _coroutine_stand_in_registry
    try:
        stand_in = registry[coroutine_]
    except (KeyError, TypeError):
        return
    if interface_.providedBy(stand_in):
        return coroutine_


def _curried_coroutine_factory(function, coroutine_factory_path):
    """Return a `coroutine` factory that calls the factory with function.

    This function is a bit difficult to explain.  It basically curries the
    given function into the `coroutine` factory function given by it's import
    path.  It also fully preserves the function's signature, exept for the
    first parameter, which is stripped.  It is meant to be used in decorators
    like :func:`filter_`.

    It uses a template to construct the curried factory, which is why
    *coroutine_factory_path* is given as an import path string.  E.g.
    ``'m4us.core.coroutines.filter_from_callable'``.  The use of the template
    is required to preserve the function's signature on the curried factory.

    The idea is that *coroutine_factory_path* would point to a `coroutine`
    factory like :func:`filter_from_callable` which takes a function whose
    first parameter is the message object.  The resulting factory function
    accepts all additional arguments except the first one in case the function
    requires additional arguments.

    :param function: The function to wrap.  It must accept at least one
      argument.
    :type function: :obj:`~types.FunctionType`
    :param coroutine_factory_path: The import path to the coroutine factory
      function to call.
    :type coroutine_factory_path: :obj:`str`

    :returns: A coroutine factory with the function curried into it.
    :rtype: :class:`~m4us.core.interfaces.ICoroutineFactory`

    :raises TypeError: If the given function is not a function.
    :raises ValueError: If the given function does not accept at least one
      positional argument.

    :seealso: :func:`m4us.core.utils._function_wrapper_from_template` for
      additional details.

    """
    module_path, factory_name = coroutine_factory_path.rsplit('.', 1)
    template = _COROUTINE_FACTORY_TEMPLATE.format(module_path=module_path,
      factory_name=factory_name)
    ## pylint: disable=W0212
    factory = utils._function_wrapper_from_template(function, template,
      strip_first_parameter=True)
    ## pylint: enable=W0212
    interface.alsoProvides(factory, interfaces.ICoroutineFactory)
    return factory


def init():
    """Initialize `coroutine` `interface` support.

    This function must be called before any other part of m4us is used.  It
    sets up global interface and adapter registrations neccessary for the
    proper functioning of m4us.  It has been made an explicit function in order
    to avoid import-time side-effects, which is considered bad practice.

    It is recommended that this function be called either at import time or as
    the first call in a program's main function.

    """
    ## pylint: disable=W0603
    global _coroutine_stand_in_registry
    ## pylint: enable=W0603
    if _coroutine_stand_in_registry is not None:
        return
    # All Python coroutines provide ICoroutine.
    interface.classImplements(types.GeneratorType, interfaces.ICoroutine)
    # Python coroutines cannot have extra attributes (like __provided__ used by
    # zope.interface, so an attribute stand-in can be used by getting it from
    # this registry.
    ## pylint: disable=W0212
    _coroutine_stand_in_registry = utils._ObjectStandInRegistry()
    ## pylint: enable=W0212
    interface.interface.adapter_hooks.append(_interface_adapter_hook)


def coroutine(lazy=True):
    """Decorator factory to automatically activate Python_ `coroutines`.

    Before a Python_ `coroutine` can be used, it needs to be activated by
    sending :obj:`None` as it's first `message`.  This decorator does this
    automatically.

    `Coroutines` are presumptively `lazy`.  This decorator can flag the
    given `coroutine` as not `lazy` by making it adaptable to the
    :class:`~m4us.core.interfaces.INotLazy` marker `interface`.

    This decorator also registers the function as providing
    :class:`~m4us.core.interfaces.ICoroutineFactory` and registers all
    `interfaces` implemented by the function as being provided by the
    `coroutine` that the function returns.

    :param lazy: Specifies whether or not the `coroutine` is `lazy`.
    :type lazy: :class:`bool`

    :returns: A wrapper function that will activate and return the `coroutine`
      when called.
    :rtype: :class:`~types.FunctionType`

    .. warning:: When using this decorator with the
      :func:`zope.interface.implementer` and/or :func:`zope.interface.provider`
      decorators, make sure this decorator is the outer-most one.  Otherwise
      interface declarations will get lost.

    """
    def _coroutine_factory(function, *args, **kwargs):
        """Return an activated coroutine, with/without `lazy` registration."""
        coroutine_ = function(*args, **kwargs)
        coroutine_.send(None)
        interfaces_to_provide = list(interface.implementedBy(function))
        # non-lazy Python coroutines need to be adapted to INotLazy.
        if not lazy:
            interfaces_to_provide.append(interfaces.INotLazy)
        if interfaces_to_provide:
            stand_in = _coroutine_stand_in_registry.register(coroutine_)
            ## pylint: disable=W0142
            interface.directlyProvides(stand_in, *interfaces_to_provide)
            ## pylint: enable=W0142
        return coroutine_

    def _coroutine_decorator(function):
        """Decorator for creating `coroutine` factories."""
        coroutine_factory = decorator.decorator(_coroutine_factory, function)
        interface.alsoProvides(coroutine_factory, interfaces.ICoroutineFactory)
        return coroutine_factory
    return _coroutine_decorator


# [[start sample_coroutine]]
@coroutine()
def sample_coroutine():
    """Pass all messages through."""
    inbox, message = (yield)
    while True:
        if is_shutdown(inbox, message):
            yield 'signal', message
            break
        ## Your code goes here.
        inbox, message = (yield 'outbox', message)
# [[end sample_coroutine]]

# The docstring for sample_coroutine is set like this so that it can include
# it's own source code in the docs.  The literalinclude directive won't work
# completely correctly if the docstring is inline.
## pylint: disable=W0622
sample_coroutine.__doc__ = """Pass all `messages` through.

    This `coroutine` is meant to provide a canonical example of what a
    `coroutine` used with this project looks like.

    Any `messages` sent to it on any `inbox` will be sent back out on it's
    ``outbox`` `outbox`.  It is also well behaved in that it will shutdown on
    any :class:`~m4us.core.interfaces.IShutdown` `message`, forwarding it on
    before quitting.

    The full code for this `coroutine` is:

    .. literalinclude:: ../../../../m4us/core/coroutines.py
        :linenos:
        :start-after: # [[start sample_coroutine]]
        :end-before: # [[end sample_coroutine]]

    :returns: A pass-through `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    .. note:: `Producers` and `filters` need a minimum of 2 :keyword:`yield`
        statements as the output of the first one is always thrown away.  The
        output of the second one is the first `message` delivered.  On the
        other hand, the first :keyword:`yield` will be the one that gets the
        first incoming `message`.

    """
## pylint: enable=W0622


@coroutine()
def null_sink():
    """Swallow all messages except :class:`~m4us.core.interfaces.IShutdown`.

    This `coroutine` can serve as an end point in a series of connected
    `coroutines`.  All `messages` sent to it, except
    :class:`~m4us.core.interfaces.IShutdown` `messages` are ignored and not
    re-emitted.

    The `coroutine` will shutdown on any
    :class:`~m4us.core.interfaces.IShutdown` `message`, forwarding it on before
    quitting.

    :returns: A null sink `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    """
    while True:
        inbox, message = (yield)
        if utils.is_shutdown(inbox, message):
            yield 'signal', message
            break


@coroutine()
def filter_from_callable(callable_, *args, **kwargs):
    """Turn an ordinary callable (function, etc.) into a proper `coroutine`.

    This is a convenience `coroutine` that turns ordinary callables (functions,
    etc.) into proper `coroutines`.  The callable is passed ``inbox``
    `messages` and it's return value is emited on ``outbox``.

    The given callable must accept at least a single positional argument, the
    incomming ``inbox`` `message`, and return whatever should be the ``outbox``
    `message` to emit.  Any additional arguments passed to this function will
    be passed to the callable each time it is called.

    Any ``control`` or non-``inbox`` `messages` sent in will be ignored and not
    passed to the callable.  Additionally, by default, if the callable returns
    :obj:`None`, the :obj:`None` will be emitted on ``outbox`` as the
    `message`.  This behaviour can be changed by passing ``suppress_none=True``
    as a keyword argument.  When *suppress_none* is True, if the callable
    returns :obj:`None`, only a plain :obj:`None` will be yielded.  This means
    that no `message` will  be passed on to any other `coroutine`.
    Non-:obj:`None` `messages` will still be emitted on the ``outbox``
    `outbox`, however.

    :param callable\_: The callable to which to pass messages.
    :type callable\_: Any callable object
    :param suppress_none: Indicate whether or not :obj:`None` should be emitted
      on the ``outbox`` `outbox`.  (Default: :obj:`True`)
    :type suppress_none: :obj:`bool`
    :param \*args: Any additional positional arguments to pass to the callable.
    :param \*\*kwargs: Any additional keyword arguments to pass to the
      callable.

    :returns: A filter `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :raises TypeError: If the given callable is not actually a callable.

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    """
    if not callable(callable_):
        raise TypeError('Argument must be a callable.')
    suppress_none = kwargs.pop('suppress_none', False)
    inbox, message = (yield)
    while True:
        if is_shutdown(inbox, message):
            yield 'signal', message
            break
        if inbox != 'inbox':
            inbox, message = (yield)
            continue
        message = callable_(message, *args, **kwargs)
        if interfaces.IShutdown(message, False):
            yield 'signal', message
            break
        if message is None and suppress_none:
            inbox, message = (yield)
        else:
            inbox, message = (yield 'outbox', message)


def filter_(function):
    """Decorator to turn an ordinary function into a proper `coroutine`.

    This decorator returns a factory function that when called, just calls
    :func:`filter_from_callable` and returns the result.

    Any additional arguments passed the to factory function are passed on to
    :func:`filter_from_callable`.

    The factory function is also registered as providing
    :class:`~m4us.core.interfaces.ICoroutineFactory`.

    :param function: The function to turn into a `coroutine`.  It must accept
      at least one argument.
    :type function: :class:`~types.FunctionType`

    :returns: A filter coroutine factory function.
    :rtype: :class:`~m4us.core.interfaces.ICoroutineFactory`

    :raises TypeError: If the given function is not a function.
    :raises ValueError: If the given function does not accept at least one
      positional argument.

    :seealso: :func:`filter_from_callable` for the specifics.

    """
    return _curried_coroutine_factory(function,
      'm4us.core.coroutines.filter_from_callable')


@coroutine(lazy=False)
def producer_from_iterable(iterable):
    """Return a `producer` `coroutine` that iterates over an iterable.

    This is a convenience `coroutine` that emits ``outbox`` messages that are
    the results of iterating over an iterable.  When all the iterable results
    have been emitted, an :class:`~m4us.core.interfaces.IProducerFinished`
    messages is emitted.  Then the `producer` terminates.

    :param iterable: The iterable object over which to iterate.
    :type iterable: Any iterable

    :returns: A non-lazy producer `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :raises TypeError: If the given object is not an iterable or it does not
      produce a valid iterator.

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    """
    iterator = iter(iterable)
    inbox, message = (yield)
    for element in iterator:
        if is_shutdown(inbox, message):
            yield 'signal', message
            return
        inbox, message = (yield 'outbox', element)
    yield 'signal', messages.ProducerFinished()


def producer(generator_factory):
    """Decorator that turns a generator function into a `producer` `coroutine`.

    This decorator returns a factory function that when called, just calls the
    generator function and passes the result to :func:`producer_from_iterable`,
    returning the result.

    Any additional arguments passed the to factory function are passed on to
    to the generator factory.

    The factory function is also registered as providing
    :class:`~m4us.core.interfaces.ICoroutineFactory`.

    :param generator_factory: The generator function to turn into a `producer`.
    :type function: :class:`~types.FunctionType`

    :returns: A `producer` `coroutine` factory function.
    :rtype: :class:`~m4us.core.interfaces.ICoroutineFactory`

    :raises TypeError: If the given generator factory is not a callable.

    .. note:: Technically this decorator will work with any function that
        returns an iterable.  A generator function is not strictly required,
        though that is the expected typical use case.

    :seealso: :func:`producer_from_iterable` for the specifics.

    """
    def _producer_factory(generator_factory, *args, **kwargs):
        """Return a `producer` `coroutine` from the iterable factory."""
        generator = generator_factory(*args, **kwargs)
        return producer_from_iterable(generator)
    if not callable(generator_factory):
        raise TypeError('Argument must be a callable that returns an iterable')
    producer_factory = decorator.decorator(_producer_factory,
      generator_factory)
    interface.alsoProvides(producer_factory, interfaces.ICoroutineFactory)
    return producer_factory


@interface.provider(interfaces.ICoroutineFactory)
def sink_from_callable(callable_, *args, **kwargs):
    """Turn an ordinary callable (function, etc.) into a `sink` `coroutine`.

    This is a convenience function that turns ordinary callables (functions,
    etc.) into `sink` `coroutines`.  The callable is passed ``inbox``
    `messages` and it's return value suppressed, unless it is an
    :class:`~m4us.core.interfaces.IShutdown` message.

    The given callable must accept at least a single positional argument, the
    incomming ``inbox`` `message`, and return nothing.  It may return an
    :class:`~m4us.core.interfaces.IShutdown` message, however, if appropriate,
    but it should not normally be necessary.  Any additional arguments passed
    to this function will be passed to the callable each time it is called.

    Any ``control`` or non-``inbox`` `messages` sent in will be ignored and not
    passed to the callable.

    :param callable\_: The callable to which to pass messages.
    :type callable\_: Any callable object
    :param \*args: Any additional positional arguments to pass to the callable.
    :param \*\*kwargs: Any additional keyword arguments to pass to the
      callable.

    :returns: A `sink` `coroutine`
    :rtype: :class:`~types.GeneratorType`

    :raises TypeError: If the given callable is not actually a callable.

    :Implements: :class:`~m4us.core.interfaces.ICoroutine`
    :Provides: :class:`~m4us.core.interfaces.ICoroutineFactory`

    """
    def _sink_from_callable(*args, **kwargs):
        """Return a `sink` `coroutine` from that calls the callable."""
        result = callable_(*args, **kwargs)
        if interfaces.IShutdown(result, False):
            return result
    if not callable(callable_):
        raise TypeError('Argument must be a callable.')
    kwargs.pop('suppress_none', None)
    return filter_from_callable(_sink_from_callable, suppress_none=True, *args,
      **kwargs)


def sink(function):
    """Decorator to turn an ordinary function into a `sink` `coroutine`.

    This decorator returns a factory function that when called, just calls
    :func:`sink_from_callable` and returns the result.

    Any additional arguments passed the to factory function are passed on to
    :func:`sink_from_callable`.

    The factory function is also registered as providing
    :class:`~m4us.core.interfaces.ICoroutineFactory`.

    :param function: The function to turn into a `sink` `coroutine`.  It must
      accept at least one argument.
    :type function: :class:`~types.FunctionType`

    :returns: A `sink` `coroutine` factory function.
    :rtype: :class:`~m4us.core.interfaces.ICoroutineFactory`

    :raises TypeError: If the given function is not a function.
    :raises ValueError: If the given function does not accept at least one
      positional argument.

    :seealso: :func:`sink_from_callable` for the specifics.

    """
    return _curried_coroutine_factory(function,
      'm4us.core.coroutines.sink_from_callable')


#---Classes--------------------------------------------------------------------


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
