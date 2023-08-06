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


"""Support functions and classes for m4us tests."""


#---Imports--------------------------------------------------------------------

#---  Standard library imports
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
## pylint: disable=W0622, W0611
from future_builtins import ascii, filter, hex, map, oct, zip
## pylint: enable=W0622, W0611

import glob
from os import path
import re
import types
import contextlib

#---  Third-party imports
import unittest2
import decorator
import pkg_resources
## pylint: disable=E0611
from zope import interface
## pylint: disable=F0401
from zope.interface import verify, exceptions
## pylint: enable=E0611, F0401
from unittest2 import loader, runner

#---  Project imports
from m4us.core import utils


#---Globals--------------------------------------------------------------------

_DEFAULT_MODULE_EXCLUDES = ('__init__', 'api')
_DEFAULT_OBJECT_EXCLUDES = utils._DEFAULT_NAME_EXCLUDES
# There will probably be a localization issue here under Python 3, but I don't
# know how to solve it yet and it likely will not come up in this project.
_CAPITAL_LETTERS = re.compile('([A-Z])')


#---Functions------------------------------------------------------------------

@decorator.decorator
def memoize(func, *args, **kwargs):
    # This decorator was taken from an example in the decorator package
    # documentation.  Thanks Michele Simionato!
    if kwargs:
        # frozenset is used to ensure hashability
        key = args, frozenset(kwargs.iteritems())
    else:
        key = args
    if not hasattr(func, 'cache'):
        func.cache = {}
    cache = func.cache
    if key in cache:
        return cache[key]
    else:
        cache[key] = result = func(*args, **kwargs)
        return result


def run_tests(start_dir='', verbosity=1):
    """Run all m4us tests starting in the given package-relative directory.

    start_dir should always be a relative sub-directory of the m4us package
    (e.g. 'core' for 'm4us/core' or 'core/tests' for 'm4us/core/tests').  The
    default is the root of the m4us package itself (i.e. 'm4us').

    verbosity: 0 = no dots, only totals; 1 = dots and totals, no test names;
    2 = full test names and totals, no dots.

    """
    package = 'm4us'
    start_dir = pkg_resources.resource_filename(package, start_dir)
    top_level_dir = pkg_resources.resource_filename(package, '')
    tests = loader.TestLoader().discover(start_dir,
      top_level_dir=top_level_dir)
    runner.TextTestRunner(verbosity=verbosity).run(tests)


#---Classes--------------------------------------------------------------------

class _Alias(object):

    """Descriptor that provides an alias to another attribute on the object."""

    def __init__(self, real_name):
        self.real_name = real_name

    def __get__(self, object_, type_=None):
        return getattr(object_, self.real_name)

    def __set__(self, object_, value):
        setattr(object_, self.real_name, value)

    def __repr__(self):
        return '<_Alias({0.real_name!r})>'.format(self)


class _PEP8Meta(type):

    """Meta-class that converts all non-pep8 attribute names to pep8.

    This meta-class puts the original objects under the pep8 names and creates
    aliases for all the non-pep8 names for API compatibility.

    A class using this meta-class can override the default pep8 name choices by
    adding a class attribute called __pep8_overrides__ that is a tuple of
    2-tuples in the form of (original_name, pep8_name).  This attribute will be
    read by the meta-class and removed from the actual class before it is
    created.

    .. note:: This meta-class does not affect sub-classes, only the class on
        which it was directly applied.

    """

    def __new__(mcs, name, bases, namespace):
        """Create the new class, pepifying attribute is appropriate."""
        # Don't pepify sub-classes.
        if '__metaclass__' in namespace and namespace['__metaclass__'] is mcs:
            mcs._pepify(bases, namespace)
        return type.__new__(mcs, name, bases, namespace)

    @classmethod
    def _pepify(mcs, bases, namespace):
        """Override all non-pep8 names in bases with pep8 version and aliases.

        For every attribute of every base class, if it has upper case letters
        in it, convert them to lowercase with leading underscores.

        This is done by adding the original attribute objects to the class
        namespace under the pep8 name and adding alias descriptors under the
        non-pep8 name.  This preserved API compatibility, but also allows
        sub-classes to override pep8-named attributes and have the non-pep8
        attributes automatically use the replacements.

        Additionally, the pep8 names for certain attributes can be overridden
        by adding a __pep8_overrides__ class attribute to the class.  See this
        meta-class' docstring for more details.

        """
        # pep8ifying logic inspired by nose.tools.  Thanks Jason Pellerin!
        to_lower_with_underscore = lambda match: '_' + \
          match.groups()[0].lower()
        if '__pep8_overrides__' in namespace:
            overrides = dict(namespace['__pep8_overrides__'])
            del namespace['__pep8_overrides__']
        else:
            overrides = {}
        for base in bases:
            for name, object_ in vars(base).items():
                if '_' in name:
                    continue
                if name in overrides:
                    pep8_name = overrides[name]
                else:
                    pep8_name = _CAPITAL_LETTERS.sub(to_lower_with_underscore,
                      name)
                if name == pep8_name:
                    continue
                namespace[bytes(pep8_name)] = object_
                namespace[name] = _Alias(pep8_name)


class _AssertNotRaisesContext(object):
    """A context manager used to implement TestCase.assertNotRaises method."""

    # _AssertNotRaisesContext is basically a modified copy of
    # _AssertRaisesContext from unittest2 (v.0.4.0).  unittest2 is marked at
    # being under the "Classifier: License :: OSI Approved :: BSD License"  in
    # it's PKG-INFO, but does not actually include any license text in the
    # source archive.  Since unittest2 is just a back-port of the unittest
    # module in Python 2.7, I (Krys Lawrence) am interpreting the licence of
    # unittest2 to be the BSD License as defined by the OSI.  It's text being
    # at: http://www.opensource.org/licenses/bsd-license.php.  This
    # interpretation is, I believe, consistent with the spirit of the Python
    # community's licensing preferences and with that of Michael Foord
    # (unittest2's author) as well.
    #
    # All that to say that I believe it is safe to include this code in this
    # project.

    # Preserving unittest2 codestyle.
    ## pylint: disable=C0103, W0201

    def __init__(self, expected, test_case):
        self.expected = expected
        self.failureException = test_case.failureException

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            return False
        self.exception = exc_value  # store for later retrieval
        if not issubclass(exc_type, self.expected):
            # let unexpected exceptions pass through
            return False
        try:
            exc_name = self.expected.__name__
        except AttributeError:
            exc_name = str(self.expected)
        raise self.failureException(
            "%s raised" % (exc_name,))


class TestCase(unittest2.TestCase, object):

    """unittest2 TestCase class but with pep8-compliant attributes.

    This class is a sub-class of unittest2 TestCase that is a new-style class
    and provides pep8-compliant attribute and method names.  (i.e.
    ``self.assert_true()`` instead of ``self.assertTrue()``.

    The original non-pep8 names are still provided for API compatibility, but
    they are now just alias descriptors to the pep8 attributes.

    Additionally, unittest2's default of treating unicode strings as multi-line
    strings has been removed since it leads to ugly and inconsistent error
    output for non-multi-line unicode strings.

    """

    # Preserving unittest2 codestyle.
    ## pylint: disable=C0103

    __metaclass__ = _PEP8Meta
    # This attribute overrides the pep8 names for specific attributes.
    __pep8_overrides__ = (
      ('setUp', 'setup'),
      ('tearDown', 'teardown'),
      ('setUpClass', 'setup_class'),
      ('tearDownClass', 'teardown_class'),
    )

    assertNotRaises = _Alias('assert_not_raises')

    def __init__(self, methodName='runTest'):
        """See class docstring for details about this method."""
        unittest2.TestCase.__init__(self, methodName)
        del self._type_equality_funcs._store[unicode]

    def assert_not_raises(self, excClass, callableObj=None, *args, **kwargs):
        """Fail if an exception of class excClass is thrown
           by callableObj when invoked with arguments args and keyword
           arguments kwargs. If a different type of exception is
           thrown, it will not be caught, and the test case will be
           deemed to have suffered an error, exactly as for an
           unexpected exception.

           If called with callableObj omitted or None, will return a
           context object used like this::

                with self.assertNotRaises(SomeException):
                    do_something()

           The context manager keeps a reference to the exception as
           the 'exception' attribute. This allows you to inspect the
           exception after the assertion::

               with self.assertNotRaises(SomeException) as cm:
                   do_something()
               the_exception = cm.exception
               self.assertEqual(the_exception.error_code, 3)
        """
        # This method is basically a modified copy of the assertRaises() method
        # in Michael Foord's unittest2 package.  See the big comment in the
        # above _AssertNotRaisesContext class for details on why I (Krys
        # Lawrence) believe it is safe to include in this project.
        if callableObj is None:
            return _AssertNotRaisesContext(excClass, self)
        try:
            callableObj(*args, **kwargs)
        except excClass:
            if hasattr(excClass, '__name__'):
                excName = excClass.__name__
            else:
                excName = str(excClass)
            raise self.failureException, "%s raised" % excName


class CommonTestBase(object):

    def _get_sut(self):
        raise NotImplementedError

    def _get_required_args(self):
        return ()

    def _get_required_kwargs(self):
        return {}

    def _get_sut_interfaces(self):
        return ()

    def _get_result_interfaces(self):
        return ()

    def _call_sut(self, *new_args, **new_kwargs):
        sut = self._get_sut()
        args = (new_args if new_args else self._get_required_args())
        kwargs = self._get_required_kwargs()
        kwargs.update(new_kwargs)
        return sut(*args, **kwargs)

    def setup(self):
        import m4us
        m4us.init()

    def assert_interfaces(self, object_, interfaces, check_function=None):
        # Python coroutines cannot directly provide interfaces, but have been
        # set up to provide them through adaptation.  This bit just makes it
        # transparent to the interface verification tests.
        if isinstance(object_, types.GeneratorType):
            self.assert_adapted_interfaces(object_, interfaces, check_function)
            return
        if check_function is None:
            check_function = verify.verifyObject
        with self.assert_not_raises(exceptions.Invalid):
            for interface_ in interfaces:
                check_function(interface_, object_)

    def assert_adapted_interfaces(self, object_, interfaces,
      check_function=None):
        if check_function is None:
            check_function = verify.verifyObject
        with contextlib.nested(
          self.assert_not_raises(exceptions.Invalid),
          self.assert_not_raises(TypeError)
          ):
            for interface_ in interfaces:
                adapted = interface_(object_)
                check_function(interface_, adapted, tentative=1)

    def assert_class_interfaces(self, class_, interfaces):
        self.assert_interfaces(class_, interfaces, verify.verifyClass)


class ObjectShouldProvideInterface(CommonTestBase):

    ## pylint: disable=W0223

    def test_it_should_provide_required_interfaces(self):
        interfaces = self._get_sut_interfaces()
        if not interfaces:
            self.skip_test('No SUT interfaces required.')
        sut = self._get_sut()
        self.assert_interfaces(sut, interfaces)

    def test_result_should_provide_required_interfaces(self):
        interfaces = self._get_result_interfaces()
        if not interfaces:
            self.skip_test('No result interfaces required.')
        result = self._call_sut()
        self.assert_interfaces(result, interfaces)


class ClassShouldProvideAndImplementInterface(ObjectShouldProvideInterface):

    ## pylint: disable=W0223

    def test_it_should_implement_required_result_interfaces(self):
        interfaces = self._get_result_interfaces()
        if not interfaces:
            self.skip_test('No result interfaces required.')
        class_ = self._get_sut()
        self.assert_class_interfaces(class_, interfaces)


class APIModuleShouldIncludeAllPublicObjects(CommonTestBase):

    def _get_base_package(self):
        raise NotImplementedError

    def _get_module_excludes(self):
        return _DEFAULT_MODULE_EXCLUDES

    def _get_object_excludes(self):
        return _DEFAULT_OBJECT_EXCLUDES

    def assert_object_name_in_module(self, module, object_path):
        """Assert that the object name is in module as well as it's __all__.

        The object name is extracted as the last segment of the object path.

        """
        object_name = object_path.rsplit('.', 1)[-1]
        message_vars = (object_path, module.__name__)
        self.assert_true(hasattr(module, object_name),
          '"{0}" missing from "{1}" module.'.format(*message_vars))
        self.assert_true(object_name in module.__all__,
          '"{0}" missing from "{1}.__all__".'.format(*message_vars))

    def test_it(self):
        # Test that all public objects in base_package are in module.
        # This method searches all sub-modules of the base package and tests
        # that all public objects in all the modules are found in the module to
        # check.  It skips any modules and objects that are listed in the
        # exclude methods.
        module = self._get_sut()
        base_package = self._get_base_package()
        module_excludes = self._get_module_excludes()
        object_excludes = self._get_object_excludes()
        source_module_glob_pattern = path.join(base_package.__path__[0],
          b'*.py')
        module_excludes = set(module_excludes)
        for source_module_path in glob.glob(source_module_glob_pattern):
            source_module_name = path.splitext(path.basename(
              source_module_path))[0]
            if source_module_name in module_excludes:
                continue
            from_namespace = __import__(base_package.__name__, fromlist=[
              source_module_name])
            source_module = getattr(from_namespace, source_module_name)
            for object_name in utils._public_object_names(vars(source_module),
              object_excludes):
                object_path = '{0}.{1}'.format(source_module_name, object_name)
                self.assert_object_name_in_module(module, object_path)


class IDummy(interface.Interface):

    pass


class IDummyFactory(interface.Interface):

    pass


class DummyException(Exception):

    pass


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
