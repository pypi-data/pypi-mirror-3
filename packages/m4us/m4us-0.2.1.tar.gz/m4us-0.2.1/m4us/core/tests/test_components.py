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


"""Tests for m4us.core.components."""


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
import unittest2
## pylint: disable=E0611
from zope import interface
## pylint: disable=F0401
from zope.interface import verify
## pylint: enable=E0611, F0401

#---  Project imports
from m4us.core.tests import support, test_coroutines


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

def make_basic_component_class():
    from m4us.core import components, interfaces

    class BasicComponent(components.Component):

        interface.classProvides(interfaces.ICoroutineFactory)

        def _main(self):
            return test_coroutines.plain_coroutine()

    return BasicComponent


#---Classes--------------------------------------------------------------------

class ComponentShouldProvideICoroutine(
  test_coroutines.CoroutineShouldProvideICoroutine,
  support.ClassShouldProvideAndImplementInterface):

    pass


class ComponentShouldAcceptKeywordArguments(support.CommonTestBase):

    def test_it_should_accept_keyword_arguments(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(foo='bar', bat='baz')

    def test_it_should_set_keyword_arguments_as_attributes(self):
        component = self._call_sut(foo='bar', bat='baz')
        self.assert_true(hasattr(component, 'foo'))
        self.assert_equal(component.foo, 'bar')
        self.assert_true(hasattr(component, 'bat'))
        self.assert_equal(component.bat, 'baz')


class ComponentShouldSupportAnInternalCoroutine(
  test_coroutines.CoroutineTestBase):

    def _get_icoroutine_interface(self):
        from m4us.core import interfaces
        return interfaces.ICoroutine

    def test_it_should_initialize_the_contained_coroutine(self):
        component = self._call_sut()
        message = self._get_messages()[0]
        response = self._get_responses()[0]
        self.assert_true(hasattr(component, '_coroutine'))
        with self.assert_not_raises(TypeError):
            self.assert_equal(response, component._coroutine.send(message))

    def test_main_should_return_an_icoroutine(self):
        component = self._call_sut()
        icoroutine_interface = self._get_icoroutine_interface()
        verify.verifyObject(icoroutine_interface, component._main())


#---  Raw Component tests

class RawComponentTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import components
        return components.Component


class TestRawComponentShouldProvideICoroutine(RawComponentTestBase,
  ComponentShouldProvideICoroutine, support.TestCase):

    test_result_should_provide_required_interfaces = None


class TestRawComponentShouldNotProvideMain(RawComponentTestBase,
  support.TestCase):

    def test_default_main_should_raise_notimplementederror(self):
        with self.assert_raises(NotImplementedError):
            self._call_sut()


#---  Basic Component tests

class BasicComponentTestBase(test_coroutines.BasicMessagesMixin,
  test_coroutines.CoroutineTestBase):

    def _get_sut(self):
        return make_basic_component_class()


class TestBasicComponentShouldProvideICoroutine(BasicComponentTestBase,
  ComponentShouldProvideICoroutine, support.TestCase):

    pass


class TestBasicComponentShouldAcceptAndEmitMessages(BasicComponentTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestBasicComponentShouldSupportThrowingExceptions(BasicComponentTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestBasicComponentShouldSupportDelayedExceptions(BasicComponentTestBase,
  test_coroutines.CoroutineShouldSupportDelayedExceptions, support.TestCase):

    pass


class TestBasicComponentShouldSupportBeingClosed(BasicComponentTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestBasicComponentShouldAcceptKeywordArguments(BasicComponentTestBase,
  ComponentShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestBasicComponentShouldAnInternalCoroutine(BasicComponentTestBase,
  ComponentShouldSupportAnInternalCoroutine, support.TestCase):

    pass


#---  SampleComponent tests

class SampleComponentTestBase(test_coroutines.CoroutineTestBase):

    def _get_sut(self):
        from m4us.core import components
        return components.SampleComponent


class TestSampleComponentShouldProvideICoroutine(SampleComponentTestBase,
  ComponentShouldProvideICoroutine, support.TestCase):

    pass


class TestSampleComponentShouldAcceptAndEmitMessages(SampleComponentTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestSampleComponentShouldSupportThrowingExceptions(
  SampleComponentTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestSampleComponentShouldSupportBeingClosed(SampleComponentTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestSampleComponentShouldRespondToShutdownMessages(
  SampleComponentTestBase,
  test_coroutines.CoroutineShouldRespondToShutdownMessages, support.TestCase):

    pass


class TestSampleComponentShouldAcceptKeywordArguments(SampleComponentTestBase,
  ComponentShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestSampleComponentShouldAnInternalCoroutine(SampleComponentTestBase,
  ComponentShouldSupportAnInternalCoroutine, support.TestCase):

    pass


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
