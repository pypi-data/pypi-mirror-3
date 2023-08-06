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


"""Integration tests for m4us.backplane."""


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

class TestBackplaneIntegration(support.TestCase):

    def test_with_backplane_outstide_pipelines(self):
        m4us.init()
        backplane = m4us.backplane()
        publisher_1 = m4us.Pipeline(
          common.counter(5),
          ## pylint:disable=E1120
          common.doubler(),
          ## pylint:enable=E1120
          m4us.Publisher(),
        )
        source_2 = common.counter(5)
        publisher_2 = m4us.Publisher()
        subscriber_1 = common.Accumulator()
        subscriber_2 = common.Accumulator()
        post_office = m4us.PostOffice()
        all_links = [
          publisher_1.links,
          m4us.easy_link(publisher_1, backplane),
          m4us.easy_link(source_2, publisher_2, backplane),
          m4us.easy_link(backplane, subscriber_1),
          m4us.easy_link(backplane, subscriber_2),
        ]
        for links in all_links:
            post_office.register(*links)
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(backplane, source_2, publisher_2, subscriber_1,
          subscriber_2, *publisher_1.coroutines)
        scheduler.run()
        self.assert_equal([0, 0, 1, 2, 2, 3, 4, 4, 6, 8],
          sorted(subscriber_1.results_list))
        self.assert_equal(subscriber_1.results_list, subscriber_2.results_list)

    def test_with_backplane_inside_pipelines(self):
        m4us.init()
        post_office = m4us.PostOffice()
        scheduler = m4us.Scheduler(post_office, add_ignores_duplicates=True)
        backplane = m4us.backplane()
        publisher_1 = m4us.Pipeline(
          common.counter(5),
          ## pylint:disable=E1120
          common.doubler(),
          ## pylint:enable=E1120
          m4us.publish_to(backplane),
        )
        post_office.register(*publisher_1.links)
        scheduler.register(*publisher_1.coroutines)
        publisher_2 = m4us.Pipeline(
          common.counter(5),
          m4us.Publisher(),
          backplane,
          m4us.null_sink(),
        )
        post_office.register(*publisher_2.links)
        scheduler.register(*publisher_2.coroutines)
        sink_1 = common.Accumulator()
        subscriber_1 = m4us.Pipeline(
          backplane,
          sink_1,
        )
        post_office.register(*subscriber_1.links)
        scheduler.register(*subscriber_1.coroutines)
        sink_2 = common.Accumulator()
        subscriber_2 = m4us.Pipeline(
          backplane,
          sink_2,
        )
        post_office.register(*subscriber_2.links)
        scheduler.register(*subscriber_2.coroutines)
        scheduler.run()
        self.assert_equal([0, 0, 2, 1, 4, 2, 6, 3, 8, 4], sink_1.results_list)
        self.assert_equal(sink_1.results_list, sink_2.results_list)


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
