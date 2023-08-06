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


"""Tests for m4us.core.utils."""


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
import unittest2
import mock
import decorator

#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  easy_link tests

class _EasyLinkTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import utils
        return utils.easy_link

    def _make_mock_coroutines(self):
        return [mock.Mock() for _ in xrange(5)]


class TestEasyLinkShouldLinkMailboxes(_EasyLinkTestBase, support.TestCase):

    def test_it_should_link_outboxes_inboxes_signals_and_controls(self):
        coroutines = self._make_mock_coroutines()
        links = self._call_sut(*coroutines)
        self.assert_equal(len(links), (len(coroutines) - 1) * 2)
        for source, sink in zip(coroutines, coroutines[1:]):
            self.assert_in((source, 'outbox', sink, 'inbox'), links)
            self.assert_in((source, 'signal', sink, 'control'), links)


class TestEasyLinkShouldReturnLinks(_EasyLinkTestBase, support.TestCase):

    def _make_post_office(self):
        from m4us.core import postoffices
        return postoffices.PostOffice()

    def _get_link_exists_error(self):
        from m4us.core import exceptions
        return exceptions.LinkExistsError

    def test_it_should_return_links_compatible_with_ipostoffice(self):
        post_office = self._make_post_office()
        link_exists_error = self._get_link_exists_error()
        coroutines = self._make_mock_coroutines()
        links = self._call_sut(*coroutines)
        with self.assert_not_raises(TypeError):
            with self.assert_not_raises(link_exists_error):
                post_office.register(*links)


#---  is_shutdown tests

class _IsShutdownTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import utils
        return utils.is_shutdown

    def _make_shutdown_message(self):
        from m4us.core import messages
        return messages.Shutdown()


class TestIsShutdownShouldReturnTrueOnIShutdownMessage(_IsShutdownTestBase,
  support.TestCase):

    def test_it_should_return_true_if_control_and_ishutdown(self):
        shutdown_message = self._make_shutdown_message()
        result = self._call_sut('control', shutdown_message)
        self.assert_true(result)

    def test_it_should_return_false_if_inbox_is_not_control(self):
        shutdown_message = self._make_shutdown_message()
        result = self._call_sut('uncontrol', shutdown_message)
        self.assert_false(result)

    def test_it_should_return_false_if_message_is_not_ishutdown(self):
        result = self._call_sut('uncontrol', 'not shutdown')
        self.assert_false(result)


class TestIsShutdownShouldAllowAlternateInboxs(_IsShutdownTestBase,
  support.TestCase):

    def test_it_should_allow_overriding_of_the_inbox_name(self):
        shutdown_message = self._make_shutdown_message()
        result = self._call_sut('changed_inbox', shutdown_message,
          expected_inbox='changed_inbox')
        self.assert_true(result)


#--- _ObjectStandInRegistry tests

class _ObjectStandInRegistryTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import utils
        return utils._ObjectStandInRegistry

    def _make_object(self):
        return mock.Mock()


class TestOjectStandInRegisteryShouldAcceptRegistrations(
  _ObjectStandInRegistryTestBase, support.TestCase):

    #---  register tests

    def test_register_should_register_an_object(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        self.assert_true(registry.is_registered(object_))

    def test_register_should_return_the_object_stand_in(self):
        registry = self._call_sut()
        object_ = self._make_object()
        stand_in = registry.register(object_)
        self.assert_is_not_none(stand_in)

    def test_register_should_be_idempotent(self):
        registry = self._call_sut()
        object_ = self._make_object()
        stand_in_1 = registry.register(object_)
        with self.assert_not_raises(Exception):
            stand_in_2 = registry.register(object_)
        self.assert_is(stand_in_1, stand_in_2)

    #---  is_registered tests

    def test_is_registered_should_return_true_if_object_is_registered(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        self.assert_true(registry.is_registered(object_))

    def test_is_registered_should_return_false_if_object_not_registered(self):
        registry = self._call_sut()
        object_ = self._make_object()
        self.assert_false(registry.is_registered(object_))


class TestOjectStandInRegisteryShouldAllowUnregistrations(
  _ObjectStandInRegistryTestBase, support.TestCase):

    #---  clear tests

    def test_clear_should_erase_all_registrations(self):
        registry = self._call_sut()
        objects = [self._make_object() for _ in range(10)]
        for object_ in objects:
            registry.register(object_)
            self.assert_true(registry.is_registered(object_))
        registry.clear()
        for object_ in objects:
            self.assert_false(registry.is_registered(object_))

    #---  unregister tests

    def test_unregister_should_unregister_an_object(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        self.assert_true(registry.is_registered(object_))
        registry.unregister(object_)
        self.assert_false(registry.is_registered(object_))

    def test_unregister_should_do_nothing_if_object_was_never_registered(self):
        registry = self._call_sut()
        object_ = self._make_object()
        with self.assert_not_raises(Exception):
            registry.unregister(object_)

    def test_unregister_should_be_idempotent(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        self.assert_true(registry.is_registered(object_))
        registry.unregister(object_)
        self.assert_false(registry.is_registered(object_))
        with self.assert_not_raises(Exception):
            registry.unregister(object_)

    #---  __delitem__ tests

    def test_delitem_should_unregister_an_object(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        self.assert_true(registry.is_registered(object_))
        del registry[object_]
        self.assert_false(registry.is_registered(object_))


class TestOjectStandInRegisteryShouldProvideStandInObjects(
  _ObjectStandInRegistryTestBase, support.TestCase):

    def _get_stand_in_class(self):
        from m4us.core import utils
        return utils._ObjectStandIn

    #---  _ObjectStandIn tests

    def test_stand_in_should_be_instance_of_stand_in_class(self):
        registry = self._call_sut()
        object_ = self._make_object()
        stand_in_class = self._get_stand_in_class()
        stand_in = registry.register(object_)
        self.assert_is_instance(stand_in, stand_in_class)

    def test_stand_in_should_accept_new_attributes(self):
        registry = self._call_sut()
        object_ = self._make_object()
        stand_in = registry.register(object_)
        with self.assert_not_raises(AttributeError):
            stand_in.some_new_attribute = 'some_value'
        self.assert_equal(stand_in.some_new_attribute, 'some_value')

    #---  get_stand_in tests

    def test_get_stand_in_should_return_the_stand_in(self):
        registry = self._call_sut()
        object_ = self._make_object()
        stand_in_1 = registry.register(object_)
        stand_in_2 = registry.get_stand_in(object_)
        self.assert_is(stand_in_2, stand_in_1)

    def test_get_stand_in_should_raise_valueerror_if_object_was_not_registered(
      self):
        registry = self._call_sut()
        object_ = self._make_object()
        with self.assert_raises(ValueError):
            registry.get_stand_in(object_)

    #---  __getitem__ tests

    def test_getitem_should_return_the_stand_in(self):
        registry = self._call_sut()
        object_ = self._make_object()
        registry.register(object_)
        stand_in_1 = registry.get_stand_in(object_)
        stand_in_2 = registry[object_]
        self.assert_is(stand_in_2, stand_in_1)

    def test_getitem_should_raise_keyerror_if_object_was_not_registered(self):
        registry = self._call_sut()
        object_ = self._make_object()
        with self.assert_raises(KeyError):
            ## pylint: disable=W0104
            registry[object_]
            ## pylint: enable=W0104


#---  _strip_first_parameter tests

class TestStripFirstParameter(support.CommonTestBase, support.TestCase):

    def _get_sut(self):
        from m4us.core import utils
        return utils._strip_first_parameter

    def _make_function_maker(self, function):
        return decorator.FunctionMaker(function)

    def test_it_should_accept_a_function_maker_argument(self):
        function_maker = self._make_function_maker(lambda required: None)
        with self.assert_not_raises(TypeError):
            self._call_sut(function_maker)

    def test_it_should_do_nothing_when_no_args(self):
        function = lambda: None
        original_function_maker = self._make_function_maker(function)
        function_maker = self._make_function_maker(function)
        self._call_sut(function_maker)
        for attribute_name in ('args', 'varargs', 'varkw', 'signature',
          'defaults'):
            original_attribute = getattr(original_function_maker,
              attribute_name)
            attribute = getattr(function_maker, attribute_name)
            self.assert_equal(attribute, original_attribute)

    def test_it_should_remove_argument_when_only_one(self):
        function_maker = self._make_function_maker(lambda one_required: None)
        self.assert_list_equal(function_maker.args, ['one_required'])
        self.assert_equal(function_maker.signature, 'one_required')
        self._call_sut(function_maker)
        self.assert_list_equal(function_maker.args, [])
        self.assert_equal(function_maker.signature, '')

    def test_it_should_preserve_signature_when_only_star_args(self):
        function_maker = self._make_function_maker(lambda *args: None)
        self.assert_equal(function_maker.varargs, 'args')
        self.assert_equal(function_maker.signature, '*args')
        self._call_sut(function_maker)
        self.assert_equal(function_maker.varargs, 'args')
        self.assert_equal(function_maker.signature, '*args')

    def test_it_should_remove_only_first_argment_when_several_exist(self):
        function_maker = self._make_function_maker(lambda first, second: None)
        self.assert_list_equal(function_maker.args, ['first', 'second'])
        self.assert_equal(function_maker.signature, 'first, second')
        self._call_sut(function_maker)
        self.assert_list_equal(function_maker.args, ['second'])
        self.assert_equal(function_maker.signature, 'second')

    def test_it_should_preserve_keyword_arguments(self):
        function_maker = self._make_function_maker(lambda first, **kwargs: 42)
        self.assert_equal(function_maker.varkw, 'kwargs')
        self.assert_equal(function_maker.signature, 'first, **kwargs')
        self._call_sut(function_maker)
        self.assert_equal(function_maker.varkw, 'kwargs')
        self.assert_equal(function_maker.signature, '**kwargs')

    def test_it_should_preserve_defaults(self):
        function_maker = self._make_function_maker(lambda first,
          other='default': None)
        self.assert_tuple_equal(function_maker.defaults, ('default',))
        self._call_sut(function_maker)
        self.assert_tuple_equal(function_maker.defaults, ('default',))

    def test_it_should_remove_first_argument_default(self):
        function_maker = self._make_function_maker(lambda first='default': 42)
        self.assert_tuple_equal(function_maker.defaults, ('default',))
        self._call_sut(function_maker)
        self.assert_is_none(function_maker.defaults)

    def test_it_should_remove_message_default_when_other_defaults_exist(self):
        function_maker = self._make_function_maker(lambda first='default1',
          other='default2': None)
        self.assert_tuple_equal(function_maker.defaults, ('default1',
          'default2'))
        self._call_sut(function_maker)
        self.assert_tuple_equal(function_maker.defaults, ('default2',))


#---  _function_wrapper_from_template tests

class FunctionWrapperFromTemplateTestBase(support.CommonTestBase):

    _TEMPLATE = 'def %(name)s(%(signature)s): return _func_(%(signature)s)'

    def _get_sut(self):
        from m4us.core import utils
        return utils._function_wrapper_from_template

    def _get_required_args(self):
        return (lambda message: message, self._TEMPLATE)


class TestFunctionWrapperFromTemplateShouldValidateInputs(
  FunctionWrapperFromTemplateTestBase, support.TestCase):

    def test_it_should_accept_a_function_as_first_argument(self):
        args = self._get_required_args()
        with self.assert_not_raises(TypeError):
            self._call_sut(lambda: None, *args[1:])

    def test_it_should_require_a_function_as_first_argument(self):
        args = self._get_required_args()
        with self.assert_raises(TypeError):
            self._call_sut('not a function', *args[1:])

    def test_it_should_accept_a_template_as_second_argument(self):
        args = self._get_required_args()
        with self.assert_not_raises(TypeError):
            self._call_sut(args[0], self._TEMPLATE)

    def test_it_should_require_a_template_as_second_argument(self):
        args = self._get_required_args()
        with self.assert_raises(TypeError):
            self._call_sut(args[0])

    def test_it_should_require_a_valid_template(self):
        args = self._get_required_args()
        with self.assert_raises(SyntaxError):
            self._call_sut(args[0], 'invalid template')


class TestFunctionWrapperFromTemplateShouldCreateWrapperFromTemplate(
  FunctionWrapperFromTemplateTestBase, support.TestCase):

    def test_it_should_return_a_wrapper_function(self):
        decorator_ = self._call_sut()
        self.assert_is_instance(decorator_, types.FunctionType)

    def test_it_should_call_functionmaker_make(self):
        with mock.patch('decorator.FunctionMaker') as mock_function_maker:
            self._call_sut()
        self.assert_true(mock_function_maker().make.called)
        self.assert_equal(mock_function_maker().make.call_args[0][0],
          self._TEMPLATE)

    def test_it_should_return_function_from_functionmker_make(self):
        wrapper_function = mock.sentinel.WRAPPER_FUNCTION
        with mock.patch('decorator.FunctionMaker') as mock_function_maker:
            mock_function_maker().make.return_value = wrapper_function
            wrapper = self._call_sut()
        self.assert_is(wrapper, wrapper_function)

    def test_wrapper_should_have_an_undecorated_attribute(self):
        function, template = self._get_required_args()
        wrapper = self._call_sut(function, template)
        self.assert_true(hasattr(wrapper, 'undecorated'))
        self.assert_is(wrapper.undecorated, function)


class TestFunctionWrapperFromTemplateShouldSupportStrippingFirstParameter(
    FunctionWrapperFromTemplateTestBase, support.TestCase):

    def test_it_should_accept_strip_first_parameter_as_third_argument(self):
        args = self._get_required_args()
        with self.assert_not_raises(TypeError):
            self._call_sut(strip_first_parameter=True)
            self._call_sut(args[0], args[1], True)

    def test_it_should_require_function_with_min_one_param_if_strip_true(self):
        template = self._get_required_args()[1]
        with self.assert_raises(ValueError):
            self._call_sut(lambda: 'no parameters', template,
              strip_first_parameter=True)

    def test_it_should_accept_a_function_with_star_args(self):
        template = self._get_required_args()[1]
        with self.assert_not_raises(TypeError):
            self._call_sut(lambda *args: args, template,
              strip_first_parameter=True)

    def test_it_should_call_strip_first_parameter_if_strip_is_true(self):
        with mock.patch('decorator.FunctionMaker') as mock_function_maker:
            with mock.patch('m4us.core.utils._strip_first_parameter') as \
              mock_strip_first_parameter:
                self._call_sut(strip_first_parameter=True)
        mock_strip_first_parameter.assert_called_once_with(
          mock_function_maker())


class TestFunctionWrapperFromTemplateShouldSetUpWrapperGlobals(
    FunctionWrapperFromTemplateTestBase, support.TestCase):

    def test_it_should_accept_keyword_arguments(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(key1=1, key2=2)

    def test_it_should_pass_function_globals_to_wrapper_globals(self):
        function = self._get_required_args()[0]
        wrapper = self._call_sut()
        self.assert_dict_contains_subset(function.__globals__,
          wrapper.__globals__)

    def test_it_should_pass_function_to_wrapper_globals(self):
        function, template = self._get_required_args()
        wrapper = self._call_sut(function, template)
        self.assert_dict_contains_subset({'_func_': function},
          wrapper.__globals__)

    def test_it_should_pass_keyword_arguments_to_wrapper_globals(self):
        wrapper = self._call_sut(key1=1, key2=2)
        self.assert_dict_contains_subset({'key1': 1, 'key2': 2},
          wrapper.__globals__)


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
