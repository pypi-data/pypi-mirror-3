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


"""Tests for m4us.core.postoffices."""


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
import mock

#---  Project imports
from m4us.core.tests import support


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

class PostOfficeTestBase(support.CommonTestBase):

    def _get_nolinkerror_class(self):
        from m4us.core import exceptions
        return exceptions.NoLinkError

    def _make_mock_link(self, source=None, outbox='outbox', sink=None,
      inbox='inbox'):
        if source is None:
            source = mock.Mock()
        if sink is None:
            sink = mock.Mock()
        return (source, outbox, sink, inbox)

    def _make_mock_links(self, count=5):
        return [self._make_mock_link() for _ in range(count)]

    def _get_source_outbox(self, link):
        return (link[0], link[1])

    def _get_sink_inbox(self, link):
        return (link[2], link[3])

    def assert_link_in_postoffice(self, link, post_office):
        source_outbox = self._get_source_outbox(link)
        sink_inbox = self._get_sink_inbox(link)
        self.assert_in(source_outbox, post_office._links)
        self.assert_in(sink_inbox, post_office._links[source_outbox])


class PostOfficeShouldProvideIPostOffice(
  support.ClassShouldProvideAndImplementInterface):

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IPostOfficeFactory,)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IPostOffice,)

    def test_it_should_accept_link_ignores_duplicates_argument(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(link_ignores_duplicates=True)

    def test_it_should_accept_unlink_ignores_missing_argument(self):
        with self.assert_not_raises(TypeError):
            self._call_sut(unlink_ignores_missing=True)


class PostOfficeShouldSupportAddingLinks(PostOfficeTestBase):

    def _get_linkexistserror_class(self):
        from m4us.core import exceptions
        return exceptions.LinkExistsError

    def test_link_should_accept_a_single_link_argument(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        with self.assert_not_raises(TypeError):
            post_office.register(link)

    def test_link_should_accept_multiple_links_in_one_call(self):
        post_office = self._call_sut()
        links = self._make_mock_links()
        with self.assert_not_raises(TypeError):
            post_office.register(*links)

    def test_link_should_raise_linkexistserror_if_link_already_exists(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        link_exists_error_class = self._get_linkexistserror_class()
        with self.assert_raises(link_exists_error_class):
            post_office.register(link, link)

    def test_link_should_not_raise_linkexistserror_if_link_is_idempotent(self):
        post_office = self._call_sut(link_ignores_duplicates=True)
        link = self._make_mock_link()
        link_exists_error_class = self._get_linkexistserror_class()
        with self.assert_not_raises(link_exists_error_class):
            post_office.register(link, link)


class PostOfficeShouldSupportRemovingLinks(PostOfficeTestBase):

    def test_unlink_should_accept_a_single_link_argument(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        post_office.register(link)
        with self.assert_not_raises(TypeError):
            post_office.unregister(link)

    def test_unlink_should_accept_multiple_links_in_one_call(self):
        post_office = self._call_sut()
        links = self._make_mock_links()
        post_office.register(*links)
        with self.assert_not_raises(TypeError):
            post_office.unregister(*links)

    def test_unlink_should_raise_nolinkerror_if_source_outbox_not_linked(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        no_link_error_class = self._get_nolinkerror_class()
        with self.assert_raises(no_link_error_class):
            post_office.unregister(link)

    def test_unlink_should_raise_nolinkerror_if_sink_inbox_not_linked(self):
        post_office = self._call_sut()
        link_1 = self._make_mock_link()
        source, outbox = self._get_source_outbox(link_1)
        # Link 2 has same source and outbox as link 1
        link_2 = self._make_mock_link(source=source, outbox=outbox)
        post_office.register(link_1)
        no_link_error_class = self._get_nolinkerror_class()
        with self.assert_raises(no_link_error_class):
            post_office.unregister(link_2)

    def test_unlink_should_not_raise_nolinkerror_if_unlink_is_idempotent(self):
        post_office = self._call_sut(unlink_ignores_missing=True)
        link = self._make_mock_link()
        no_link_error_class = self._get_nolinkerror_class()
        with self.assert_not_raises(no_link_error_class):
            post_office.unregister(link)


class PostOfficeShouldSupportPostingMessages(PostOfficeTestBase):

    def test_post_should_accept_message_if_source_outbox_matches_a_link(self):
        message = 'Some message'
        post_office = self._call_sut()
        link = self._make_mock_link()
        source, outbox = self._get_source_outbox(link)
        post_office.register(link)
        no_link_error_class = self._get_nolinkerror_class()
        with self.assert_not_raises(no_link_error_class):
            post_office.post(source, outbox, message)

    def test_post_should_raise_nolinkerror_if_source_outbox_not_linked(self):
        message = 'Some message'
        post_office = self._call_sut()
        link = self._make_mock_link()
        source, outbox = self._get_source_outbox(link)
        no_link_error_class = self._get_nolinkerror_class()
        with self.assert_raises(no_link_error_class):
            post_office.post(source, outbox, message)


class PostOfficeShouldSupportRetrievingMessages(PostOfficeTestBase):

    def _get_notasinkerror_class(self):
        from m4us.core import exceptions
        return exceptions.NotASinkError

    def test_retrieve_should_return_an_iterable_of_accumulated_messages(self):
        message_1, message_2 = messages = ('Some message', 'Another message')
        post_office = self._call_sut()
        link = self._make_mock_link()
        source, outbox = self._get_source_outbox(link)
        sink, inbox = self._get_sink_inbox(link)
        post_office.register(link)
        post_office.post(source, outbox, message_1)
        post_office.post(source, outbox, message_2)
        for inbox_and_message, expected_message in zip(post_office.retrieve(
          sink), messages):
            self.assert_equal(inbox_and_message, (inbox, expected_message))

    def test_retrieve_should_return_an_empty_iterable_if_no_messages(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        sink = self._get_sink_inbox(link)[0]
        post_office.register(link)
        # Retrieve returns an iterable, not necessarily a sequence.  (i.e. it
        # may not directly support len().)
        self.assert_equal(len(list(post_office.retrieve(sink))), 0)

    def test_retrieve_should_raise_notasinkerror_if_coroutine_not_a_sink(self):
        post_office = self._call_sut()
        not_a_sink_error_class = self._get_notasinkerror_class()
        with self.assert_raises(not_a_sink_error_class):
            post_office.retrieve(mock.Mock())

    def test_retrieve_should_return_remaining_messages_after_unlink(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        message = 'Some message'
        source, outbox = self._get_source_outbox(link)
        sink, inbox = self._get_sink_inbox(link)
        post_office.register(link)
        post_office.post(source, outbox, message)
        post_office.unregister(link)
        not_a_sink_error_class = self._get_notasinkerror_class()
        with self.assert_not_raises(not_a_sink_error_class):
            # First call after unlink returns any left over messages.
            messages = post_office.retrieve(sink)
        self.assert_items_equal(messages, [(inbox, message)])

    def test_retrieve_should_raise_notasinkerror_if_coroutine_unlinked(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        sink, _ = self._get_sink_inbox(link)
        post_office.register(link)
        post_office.unregister(link)
        # First call after unlink returns any left over messages.
        post_office.retrieve(sink)
        not_a_sink_error_class = self._get_notasinkerror_class()
        with self.assert_raises(not_a_sink_error_class):
            # Second call should raise the exception.
            post_office.retrieve(sink)

    def test_retrieve_should_empty_message_queue(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        message = 'Some message'
        source, outbox = self._get_source_outbox(link)
        sink, _ = self._get_sink_inbox(link)
        post_office.register(link)
        post_office.post(source, outbox, message)
        post_office.retrieve(sink)
        empty_messages = post_office.retrieve(sink)
        self.assert_items_equal(empty_messages, [])


#---  PostOffice tests

class PostOfficeClassTestBase(PostOfficeTestBase):

    def _get_sut(self):
        from m4us.core import postoffices
        return postoffices.PostOffice


class TestPostOfficeClassShouldProvideIPostOffice(PostOfficeClassTestBase,
  PostOfficeShouldProvideIPostOffice, support.TestCase):

    pass


class TestPostOfficeClassShouldSupportAddingLinks(PostOfficeClassTestBase,
  PostOfficeShouldSupportAddingLinks, support.TestCase):

    def test_link_should_link_coroutine_mailboxes(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        post_office.register(link)
        self.assert_link_in_postoffice(link, post_office)

    def test_link_should_link_multiple_coroutine_mailboxes(self):
        post_office = self._call_sut()
        links = self._make_mock_links()
        post_office.register(*links)
        for link in links:
            self.assert_link_in_postoffice(link, post_office)

    def test_link_should_not_adapt_source_or_sink_to_an_interface(self):
        post_office = self._call_sut()
        link = ('producer', 'outbox', 'consumer', 'inbox')
        post_office.register(link)
        self.assert_link_in_postoffice(link, post_office)


class TestPostOfficeClassShouldSupportRemovingLinks(PostOfficeClassTestBase,
  PostOfficeShouldSupportRemovingLinks, support.TestCase):

    def test_unlink_should_unlink_mailboxes(self):
        post_office = self._call_sut()
        link_1 = self._make_mock_link()
        source, outbox = source_outbox = self._get_source_outbox(link_1)
        sink_inbox_1 = self._get_sink_inbox(link_1)
        # Link 2 has same source and outbox as link 1
        link_2 = self._make_mock_link(source=source, outbox=outbox)
        sink_inbox_2 = self._get_sink_inbox(link_2)
        post_office.register(link_1, link_2)
        post_office.unregister(link_1)
        self.assert_in(source_outbox, post_office._links)
        self.assert_not_in(sink_inbox_1, post_office._links[source_outbox])
        self.assert_in(sink_inbox_2, post_office._links[source_outbox])

    def test_unlink_should_unlink_multiple_coroutine_mailboxes(self):
        post_office = self._call_sut()
        links = self._make_mock_links()
        post_office.register(*links)
        post_office.unregister(*links)
        self.assert_items_equal(post_office._links, [])

    def test_unlink_should_forget_source_outboxes_with_no_links(self):
        post_office = self._call_sut()
        link = self._make_mock_link()
        post_office.register(link)
        self.assert_link_in_postoffice(link, post_office)
        post_office.unregister(link)
        source_outbox = self._get_source_outbox(link)
        self.assert_not_in(source_outbox, post_office._links)


class TestPostOfficeClassShouldSupportPostingMessages(PostOfficeClassTestBase,
  PostOfficeShouldSupportPostingMessages, support.TestCase):

    def test_post_should_store_messages(self):
        message = 'Some message'
        post_office = self._call_sut()
        link = self._make_mock_link()
        source, outbox = self._get_source_outbox(link)
        sink, inbox = self._get_sink_inbox(link)
        post_office.register(link)
        post_office.post(source, outbox, message)
        self.assert_in((inbox, message), post_office._message_queues[sink])


class TestPostOfficeClassShouldSupportRetrievingMessages(
  PostOfficeClassTestBase, PostOfficeShouldSupportRetrievingMessages,
  support.TestCase):

    pass


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

if __name__ == '__main__':
    unittest2.main()
