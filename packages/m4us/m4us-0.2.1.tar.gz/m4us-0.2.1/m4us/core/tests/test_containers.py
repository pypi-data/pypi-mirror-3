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


"""Tests for m4us.core.contatiners."""


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
from m4us.core.tests import support, test_components, test_coroutines


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  New test support infrastructure

class ContainerTestBase(test_coroutines.CoroutineTestBase):

    def _get_responses(self):
        # Overridden.
        response1 = ('_outbox_to_child', 'Hello')
        response2 = ('_outbox_to_child', 'Message 2')
        return (response1, response2)

    @support.memoize
    def _make_mock_coroutines(self, count):
        return tuple(mock.Mock() for _ in xrange(count))

    def _clear_make_mock_coroutines_cache(self):
        if hasattr(self._make_mock_coroutines.undecorated, 'cache'):
            del self._make_mock_coroutines.undecorated.cache

    def _get_coroutines(self):
        return self._make_mock_coroutines(3)

    def _get_expected_coroutines(self, container):
        return (container,) + self._get_coroutines()

    def _get_expected_links(self, container):
        raise NotImplementedError

    def _make_container_with_sub_container(self, container):
        raise NotImplementedError

    def teardown(self):
        self._clear_make_mock_coroutines_cache()


class ContainerShouldRespondToShutdownMessages(ContainerTestBase,
  test_coroutines.CoroutineShouldRespondToShutdownMessages):

    ## pylint: disable=W0223

    def assert_coroutine_shuts_down_on_message(self, container, message):
        # Overridden.
        container.send(('_control_from_child', message))
        with self.assert_raises(StopIteration):
            container.send('This should fail')

    def assert_coroutine_forwards_ishutdown_message(self, container, message):
        # Overridden.
        ishutdown_interface = self._get_ishutdown_interface()
        outbox, message = container.send(('control', message))
        self.assert_equal(outbox, '_signal_to_child')
        self.assert_true(ishutdown_interface(message, False))

    def test_it_should_forward_ishutdowns_from_child_control_to_signal(self):
        container = self._call_sut()
        shutdown_message = self._make_shutdown_message()
        ishutdown_interface = self._get_ishutdown_interface()
        outbox, message = container.send(('_control_from_child',
          shutdown_message))
        self.assert_equal(outbox, 'signal')
        self.assert_true(ishutdown_interface(message, False))


class ContainerShouldProvideIContainer(
  support.ClassShouldProvideAndImplementInterface):

    def _get_sut_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IContainerFactory,)

    def _get_result_interfaces(self):
        from m4us.core import interfaces
        return (interfaces.IContainer,)


class ContainerShouldAcceptMultiplePositionalArguments(support.CommonTestBase):

    def test_it_should_accept_multiple_positional_arguments(self):
        args = self._get_required_args()
        if not args:
            self.skip_test('No required arguments provided.')
        with self.assert_not_raises(TypeError):
            self._call_sut(*args)


class ContainerShouldSetCoroutinesAttribute(ContainerTestBase):

    ## pylint: disable=W0223

    def test_it_should_set_the_coroutines_attribute(self):
        container = self._call_sut()
        expected_coroutines = self._get_expected_coroutines(container)
        for coroutine in expected_coroutines:
            self.assert_in(coroutine, container.coroutines,
              'Expected coroutine "{0}" not found in "coroutines" '
              'attribute.'.format(repr(coroutine)))

    def test_it_should_contain_coroutines_from_sub_containers(self):
        container = self._call_sut()
        super_container = self._make_container_with_sub_container(container)
        expected_sub_coroutines = self._get_expected_coroutines(container)
        for coroutine in expected_sub_coroutines:
            self.assert_in(coroutine, super_container.coroutines)


class ContainerShouldSetLinksAttribute(ContainerTestBase):

    ## pylint: disable=W0223

    def _get_postoffice(self):
        from m4us.core import postoffices
        return postoffices.PostOffice()

    def _get_linkexistserror_class(self):
        from m4us.core import exceptions
        return exceptions.LinkExistsError

    def test_it_should_set_the_links_attribute(self):
        container = self._call_sut()
        expected_links = self._get_expected_links(container)
        for link in expected_links:
            self.assert_in(link, container.links,
              'Expected link "{0}" not found in "links" attribute.'.format(
              repr(link)))

    def test_links_should_be_compatible_with_ipostoffice(self):
        container = self._call_sut()
        post_office = self._get_postoffice()
        link_exists_error_class = self._get_linkexistserror_class()
        with self.assert_not_raises(TypeError):
            with self.assert_not_raises(link_exists_error_class):
                post_office.register(*container.links)

    def test_links_should_contain_links_from_sub_containers(self):
        container = self._call_sut()
        super_container = self._make_container_with_sub_container(container)
        expected_sub_links = self._get_expected_links(container)
        self.assert_equal(expected_sub_links, super_container.links &
          expected_sub_links)


class ContainerShouldForwardMessagesToAndFromChild(ContainerTestBase):

    ## pylint: disable=W0223

    def test_it_should_forward_inbox_messages_to_child_outbox(self):
        container = self._call_sut()
        message = self._get_messages()[0]
        response = container.send(message)
        self.assert_equal(response, ('_outbox_to_child', message[1]))

    def test_it_should_forward_control_messages_to_child_signal(self):
        container = self._call_sut()
        message = self._get_messages()[0]
        response = container.send(('control', message[1]))
        self.assert_equal(response, ('_signal_to_child', message[1]))

    def test_it_should_forward_child_inbox_messages_to_outbox(self):
        container = self._call_sut()
        message = self._get_messages()[0]
        response = container.send(('_inbox_from_child', message[1]))
        self.assert_equal(response, ('outbox', message[1]))

    def test_it_should_forward_child_control_messages_to_signal(self):
        container = self._call_sut()
        message = self._get_messages()[0]
        response = container.send(('_control_from_child', message[1]))
        self.assert_equal(response, ('signal', message[1]))


#---  Graphline tests

class GraphlineTestBase(ContainerTestBase):

    def _get_sut(self):
        from m4us.core import containers
        return containers.Graphline

    def _get_required_args(self):
        coroutine1, coroutine2, coroutine3 = self._get_coroutines()
        return (
          ('self', 'inbox', coroutine1, 'inbox'),
          ('self', 'control', coroutine1, 'control'),
          ('self', 'inbox', coroutine2, 'inbox'),
          ('self', 'control', coroutine2, 'control'),
          (coroutine2, 'outbox', coroutine3, 'inbox'),
          (coroutine2, 'signal', coroutine3, 'control'),
          (coroutine1, 'outbox', 'self', 'outbox'),
          (coroutine1, 'signal', 'self', 'signal'),
          (coroutine3, 'outbox', 'self', 'outbox'),
          (coroutine3, 'signal', 'self', 'signal'),
        )

    def _get_expected_links(self, container):
        coroutine1, coroutine2, coroutine3 = self._get_coroutines()
        return set([
          (container, '_outbox_to_child', coroutine1, 'inbox'),
          (container, '_signal_to_child', coroutine1, 'control'),
          (container, '_outbox_to_child', coroutine2, 'inbox'),
          (container, '_signal_to_child', coroutine2, 'control'),
          (coroutine2, 'outbox', coroutine3, 'inbox'),
          (coroutine2, 'signal', coroutine3, 'control'),
          (coroutine1, 'outbox', container, '_inbox_from_child'),
          (coroutine1, 'signal', container, '_control_from_child'),
          (coroutine3, 'outbox', container, '_inbox_from_child'),
          (coroutine3, 'signal', container, '_control_from_child'),
        ])

    def _make_container_with_sub_container(self, container):
        return self._get_sut()(
          ('self', 'inbox', container, 'inbox'),
          ('self', 'control', container, 'control'),
        )


class TestGraphlineShouldProvideICoroutine(GraphlineTestBase,
  test_components.ComponentShouldProvideICoroutine, support.TestCase):

    pass


class TestGraphlineShouldAcceptAndEmitMessages(GraphlineTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestGraphlineShouldSupportThrowingExceptions(GraphlineTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestGraphlineShouldSupportBeingClosed(GraphlineTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestGraphlineShouldRespondToShutdownMessages(GraphlineTestBase,
  ContainerShouldRespondToShutdownMessages, support.TestCase):

    pass


class TestGraphlineShouldAcceptKeywordArguments(GraphlineTestBase,
  test_components.ComponentShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestGraphlineShouldSupportAnInternalCoroutine(GraphlineTestBase,
  test_components.ComponentShouldSupportAnInternalCoroutine, support.TestCase):

    pass


class TestGraphlineShouldProvideIContainer(GraphlineTestBase,
  ContainerShouldProvideIContainer, support.TestCase):

    pass


class TestGraphlineShouldAcceptMultiplePositionalArguments(GraphlineTestBase,
  ContainerShouldAcceptMultiplePositionalArguments, support.TestCase):

    pass


class TestGraphlineShouldSetCoroutinesAttribute(GraphlineTestBase,
  ContainerShouldSetCoroutinesAttribute, support.TestCase):

    pass


class TestGraphlineShouldSetLinksAttribute(GraphlineTestBase,
  ContainerShouldSetLinksAttribute, support.TestCase):

    pass


class TestGraphlineShouldForwardMessagesToAndFromChild(GraphlineTestBase,
  ContainerShouldForwardMessagesToAndFromChild, support.TestCase):

    pass


class TestGraphlineShouldValidatePositionalArguments(GraphlineTestBase,
  support.TestCase):

    def _get_invalidlinkerror_class(self):
        from m4us.core import exceptions
        return exceptions.InvalidLinkError

    def test_it_should_allow_no_links_to_be_given(self):
        with self.assert_not_raises(TypeError):
            self._get_sut()()

    def test_it_should_raise_invalidlinkerror_if_self_inbox_as_inbox(self):
        source = self._get_coroutines()[0]
        invalid_link_error_class = self._get_invalidlinkerror_class()
        with self.assert_raises(invalid_link_error_class):
            self._get_sut()((source, 'outbox', 'self', 'inbox'))

    def test_it_should_raise_invalidlinkerror_if_self_control_as_inbox(self):
        source = self._get_coroutines()[0]
        invalid_link_error_class = self._get_invalidlinkerror_class()
        with self.assert_raises(invalid_link_error_class):
            self._get_sut()((source, 'signal', 'self', 'control'))

    def test_it_should_raise_invalidlinkerror_if_self_outbox_as_outbox(self):
        sink = self._get_coroutines()[0]
        invalid_link_error_class = self._get_invalidlinkerror_class()
        with self.assert_raises(invalid_link_error_class):
            self._get_sut()(('self', 'outbox', sink, 'inbox'))

    def test_it_should_raise_invalidlinkerror_if_self_signal_as_outbox(self):
        sink = self._get_coroutines()[0]
        invalid_link_error_class = self._get_invalidlinkerror_class()
        with self.assert_raises(invalid_link_error_class):
            self._get_sut()(('self', 'signal', sink, 'control'))

    def test_it_should_allow_custom_mailboxes_on_graphline_instance(self):
        # Note: We are testing both source and sink cases at once.
        graphline = self._get_sut()(('self', 'robin', 'self', 'arthur'))
        self.assert_set_equal(graphline.links, set([(graphline, 'robin',
          graphline, 'arthur')]))


#---  Pipeline tests


class PipelineTestBase(ContainerTestBase):

    def _get_sut(self):
        from m4us.core import containers
        return containers.Pipeline

    def _get_coroutines(self):
        # Overridden from IContainerTestSupportTrait.
        return self._make_mock_coroutines(5)

    def _get_required_args(self):
        return self._get_coroutines()

    def _get_expected_links(self, container):
        coroutines = self._get_coroutines()
        first_child = coroutines[0]
        last_child = coroutines[-1]
        expected_links = set([
          (container, '_outbox_to_child', first_child, 'inbox'),
          (container, '_signal_to_child', first_child, 'control'),
          (last_child, 'outbox', container, '_inbox_from_child'),
          (last_child, 'signal', container, '_control_from_child'),
        ])
        for source, sink in zip(coroutines, coroutines[1:]):
            expected_links.update([
              (source, 'outbox', sink, 'inbox'),
              (source, 'signal', sink, 'control'),
            ])
        return expected_links

    def _make_container_with_sub_container(self, container):
        return self._get_sut()(container, mock.Mock())


class TestPipelineShouldProvideICoroutine(PipelineTestBase,
  test_components.ComponentShouldProvideICoroutine, support.TestCase):

    pass


class TestPipelineShouldAcceptAndEmitMessages(PipelineTestBase,
  test_coroutines.CoroutineShouldAcceptAndEmitMessages, support.TestCase):

    pass


class TestPipelineShouldSupportThrowingExceptions(PipelineTestBase,
  test_coroutines.CoroutineShouldSupportThrowingExceptions, support.TestCase):

    pass


class TestPipelineShouldSupportBeingClosed(PipelineTestBase,
  test_coroutines.CoroutineShouldSupportBeingClosed, support.TestCase):

    pass


class TestPipelineShouldRespondToShutdownMessages(PipelineTestBase,
  ContainerShouldRespondToShutdownMessages, support.TestCase):

    pass


class TestPipelineShouldAcceptKeywordArguments(PipelineTestBase,
  test_components.ComponentShouldAcceptKeywordArguments, support.TestCase):

    pass


class TestPipelineShouldSupportAnInternalCoroutine(PipelineTestBase,
  test_components.ComponentShouldSupportAnInternalCoroutine, support.TestCase):

    pass


class TestPipelineShouldProvideIContainer(PipelineTestBase,
  ContainerShouldProvideIContainer, support.TestCase):

    pass


class TestPipelineShouldAcceptMultiplePositionalArguments(PipelineTestBase,
  ContainerShouldAcceptMultiplePositionalArguments, support.TestCase):

    pass


class TestPipelineShouldSetCoroutinesAttribute(PipelineTestBase,
  ContainerShouldSetCoroutinesAttribute, support.TestCase):

    def test_it_should_preserve_coroutine_order(self):
        for _ in xrange(10):
            pipeline = self._call_sut()
            self.assert_equal(pipeline.coroutines, (pipeline,) +
              self._get_coroutines())


class TestPipelineShouldSetLinksAttribute(PipelineTestBase,
  ContainerShouldSetLinksAttribute, support.TestCase):

    pass


class TestPipelineShouldForwardMessagesToAndFromChild(PipelineTestBase,
  ContainerShouldForwardMessagesToAndFromChild, support.TestCase):

    pass


class TestPipelineShouldValidatePositionalArguments(PipelineTestBase,
  support.TestCase):

    def test_it_should_raise_typeerror_if_no_coroutines_are_given(self):
        with self.assert_raises(TypeError):
            self._get_sut()()

    def test_it_should_raise_typeerror_if_only_one_coroutine_is_given(self):
        coroutine = self._get_coroutines()[0]
        with self.assert_raises(TypeError):
            self._get_sut()(coroutine)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------

if __name__ == '__main__':
    unittest2.main()
