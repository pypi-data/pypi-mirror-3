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


"""Tests for m4us.core.exceptions."""


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

#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class ExceptionShouldHaveADefaultMessage(support.CommonTestBase):

    def test_it_should_have_a_default_message(self):
        exception = self._call_sut()
        self.assert_true(hasattr(exception, '_message'))
        self.assert_is_instance(exception._message, unicode)


class ExceptionShouldAcceptPositionalArguments(support.CommonTestBase):

    def test_it_should_accept_a_positional_argument(self):
        exception_class = self._get_sut()
        required_kwargs = self._get_required_kwargs()
        with self.assert_not_raises(TypeError):
            exception_class('new message', **required_kwargs)

    def test_it_should_not_require_a_positional_argument(self):
        exception_class = self._get_sut()
        required_kwargs = self._get_required_kwargs()
        with self.assert_not_raises(TypeError):
            exception_class(**required_kwargs)

    def test_it_should_override_message_from_the_positional_argument(self):
        message = 'Some funky message'
        exception = self._call_sut(message)
        self.assert_equal(exception._message, message)


class ExceptionShouldAcceptKeywordArguments(support.CommonTestBase):

    def test_it_should_accept_keyword_arguments(self):
        exception_class = self._get_sut()
        required_kwargs = self._get_required_kwargs()
        with self.assert_not_raises(TypeError):
            exception_class(foo='bar', bat='baz', **required_kwargs)

    def test_it_should_store_keyword_arguments_as_attributes(self):
        kwargs = dict(a=1, b=2, c=3)
        exception = self._call_sut(**kwargs)
        for attribute, value in kwargs.items():
            self.assert_equal(getattr(exception, attribute), value)


class ExceptionShouldProvideAFormattedMessage(support.CommonTestBase):

    def test_str_should_return_valid_error_message(self):
        exception = self._call_sut()
        with self.assert_not_raises(KeyError):
            str(exception)

    def test_str_should_format_message_with_attributes(self):
        exception = self._call_sut('a={a}, b={b}, c={c}', a=1, b=2, c=3)
        self.assert_equal(str(exception), 'a=1, b=2, c=3')


#---  Core exceptions

#---  M4USException tests

class M4USExceptionTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.M4USException


class TestM4USExceptionShouldHaveADefaultMessage(M4USExceptionTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestM4USExceptionShouldAcceptPositionalArguments(M4USExceptionTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestM4USExceptionShouldAcceptKeywordArguments(M4USExceptionTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestM4USExceptionShouldProvideAFormattedMessage(M4USExceptionTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  Postoffices exceptions

#---  LinkExistsError tests

class LinkExistsErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.LinkExistsError

    def _get_required_kwargs(self):
        return dict(link='link')


class TestLinkExistsErrorShouldHaveADefaultMessage(LinkExistsErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestLinkExistsErrorShouldAcceptPositionalArguments(
  LinkExistsErrorTestBase, ExceptionShouldAcceptPositionalArguments,
  support.TestCase):

    pass


class TestLinkExistsErrorShouldAcceptKeywordArguments(LinkExistsErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestLinkExistsErrorShouldProvideAFormattedMessage(
  LinkExistsErrorTestBase, ExceptionShouldProvideAFormattedMessage,
  support.TestCase):

    pass


#---  NoLinkError tests

class NoLinkErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.NoLinkError

    def _get_required_kwargs(self):
        return dict(
          source_outbox=('source', 'outbox'),
          sink_inbox=('sink', 'inbox'),
        )


class TestNoLinkErrorShouldHaveADefaultMessage(NoLinkErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestNoLinkErrorShouldAcceptPositionalArguments(NoLinkErrorTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestNoLinkErrorShouldAcceptKeywordArguments(NoLinkErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestNoLinkErrorShouldProvideAFormattedMessage(NoLinkErrorTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  NotASinkError tests

class NotASinkErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.NotASinkError

    def _get_required_kwargs(self):
        return dict(coroutine='coroutine')


class TestNotASinkErrorShouldHaveADefaultMessage(NotASinkErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestNotASinkErrorShouldAcceptPositionalArguments(NotASinkErrorTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestNotASinkErrorShouldAcceptKeywordArguments(NotASinkErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestNotASinkErrorShouldProvideAFormattedMessage(NotASinkErrorTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  Schedulers exceptions

#---  DuplicateError tests

class DuplicateErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.DuplicateError

    def _get_required_kwargs(self):
        return dict(coroutine='coroutine')


class TestDuplicateErrorShouldHaveADefaultMessage(DuplicateErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestDuplicateErrorShouldAcceptPositionalArguments(DuplicateErrorTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestDuplicateErrorShouldAcceptKeywordArguments(DuplicateErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestDuplicateErrorShouldProvideAFormattedMessage(DuplicateErrorTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  NotAddedError tests

class NotAddedErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.NotAddedError

    def _get_required_kwargs(self):
        return dict(coroutine='coroutine')


class TestNotAddedErrorShouldHaveADefaultMessage(NotAddedErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestNotAddedErrorShouldAcceptPositionalArguments(NotAddedErrorTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestNotAddedErrorShouldAcceptKeywordArguments(NotAddedErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestNotAddedErrorShouldProvideAFormattedMessage(NotAddedErrorTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  NeverRunError tests

class NeverRunErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.NeverRunError

    def _get_required_kwargs(self):
        return dict(coroutine='coroutine')


class TestNeverRunErrorShouldHaveADefaultMessage(NeverRunErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestNeverRunErrorShouldAcceptPositionalArguments(NeverRunErrorTestBase,
  ExceptionShouldAcceptPositionalArguments, support.TestCase):

    pass


class TestNeverRunErrorShouldAcceptKeywordArguments(NeverRunErrorTestBase,
  ExceptionShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestNeverRunErrorShouldProvideAFormattedMessage(NeverRunErrorTestBase,
  ExceptionShouldProvideAFormattedMessage, support.TestCase):

    pass


#---  Containers exceptions

#---  InvalidLinkError tests

class InvalidLinkErrorTestBase(support.CommonTestBase):

    def _get_sut(self):
        from m4us.core import exceptions
        return exceptions.InvalidLinkError

    def _get_required_kwargs(self):
        return dict(
          source_outbox=('source', 'outbox'),
          sink_inbox=('sink', 'inbox'),
        )


class TestInvalidLinkErrorShouldHaveADefaultMessage(InvalidLinkErrorTestBase,
  ExceptionShouldHaveADefaultMessage, support.TestCase):

    pass


class TestInvalidLinkErrorShouldAcceptPositionalArguments(
  InvalidLinkErrorTestBase, ExceptionShouldAcceptPositionalArguments,
  support.TestCase):

    pass


class TestInvalidLinkErrorShouldAcceptKeywordArguments(
  InvalidLinkErrorTestBase, ExceptionShouldAcceptKeywordArguments,
  support.TestCase):

    pass


class TestInvalidLinkErrorShouldProvideAFormattedMessage(
  InvalidLinkErrorTestBase, ExceptionShouldProvideAFormattedMessage,
  support.TestCase):

    pass


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
