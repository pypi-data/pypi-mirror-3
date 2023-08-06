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


"""Integration tests for m4us.core.containers."""


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
import m4us.api as m4us
from m4us.core.tests import support
from m4us.core.tests.integration import common


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------


#---Classes--------------------------------------------------------------------

#---  Test classes

class TestContainerIntegration(support.TestCase):

    def test_graphline_with_source_and_sink_inside(self):
        m4us.init()
        source = common.counter(5)
        ## pylint:disable=E1120
        filter_ = common.doubler()
        ## pylint:enable=E1120
        sink1 = common.Accumulator()
        sink2 = common.Accumulator()
        graphline = m4us.Graphline(
          (source, 'outbox', sink1, 'inbox'),
          (source, 'signal', sink1, 'control'),
          (source, 'outbox', filter_, 'inbox'),
          (source, 'signal', filter_, 'control'),
          (filter_, 'outbox', sink2, 'inbox'),
          (filter_, 'signal', sink2, 'control'),
          (sink2, 'signal', 'self', 'signal'),
        )
        post_office = m4us.PostOffice()
        post_office.register(*graphline.links)
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(*graphline.coroutines)
        scheduler.run()
        self.assert_equal([0, 1, 2, 3, 4], sink1.results_list)
        self.assert_equal([0, 2, 4, 6, 8], sink2.results_list)

    def test_graphline_with_source_and_sink_outside(self):
        m4us.init()
        source = common.counter(5)
        ## pylint:disable=E1120
        filter1 = common.doubler()
        filter2 = common.doubler()
        filter3 = common.doubler()
        ## pylint:enable=E1120
        sink = common.Accumulator()
        graphline = m4us.Graphline(
          ('self', 'inbox', filter1, 'inbox'),
          ('self', 'control', filter1, 'control'),
          ('self', 'inbox', filter2, 'inbox'),
          ('self', 'control', filter2, 'control'),
          (filter2, 'outbox', filter3, 'inbox'),
          (filter2, 'signal', filter3, 'control'),
          (filter1, 'outbox', 'self', 'outbox'),
          (filter1, 'signal', 'self', 'signal'),
          (filter3, 'outbox', 'self', 'outbox'),
          (filter3, 'signal', 'self', 'signal'),
        )
        post_office = m4us.PostOffice()
        post_office.register(*graphline.links)
        post_office.register(*m4us.easy_link(source, graphline, sink))
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(source, sink, *graphline.coroutines)
        scheduler.run()
        self.assert_equal([0, 0, 2, 4, 4, 8, 6, 12, 8, 16], sink.results_list)

    def test_pipeline_with_source_and_sink_outside(self):
        m4us.init()
        source = common.counter(5)
        ## pylint:disable=E1120
        filter1 = common.doubler()
        filter2 = common.doubler()
        ## pylint:enable=E1120
        sink = common.Accumulator()
        pipeline = m4us.Pipeline(filter1, filter2)
        post_office = m4us.PostOffice()
        post_office.register(*pipeline.links)
        post_office.register(*m4us.easy_link(source, pipeline, sink))
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(source, sink, *pipeline.coroutines)
        scheduler.run()
        self.assert_equal([0, 4, 8, 12, 16], sink.results_list)

    def test_pipeline_with_source_and_sink_inside(self):
        m4us.init()
        sink = common.Accumulator()
        pipeline = m4us.Pipeline(
          common.counter(5),
          ## pylint:disable=E1120
          common.doubler(),
          ## pylint:enable=E1120
          sink,
        )
        post_office = m4us.PostOffice()
        post_office.register(*pipeline.links)
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(*pipeline.coroutines)
        scheduler.run()
        self.assert_equal([0, 2, 4, 6, 8], sink.results_list)


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
