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


"""Integration tests for m4us.core.coroutines."""


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

#--- Test classes

class TestCoroutineIntegration(support.TestCase):

    def test_pipeline_pattern(self):
        m4us.init()
        results_list = []
        source = common.counter(5)
        ## pylint:disable=E1120
        filter_ = common.doubler()
        ## pylint:disable=E1111
        sink = common.accumulator(results_list)
        ## pylint:enable=E1111, E1120
        post_office = m4us.PostOffice()
        post_office.register(*m4us.easy_link(source, filter_, sink))
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(source, filter_, sink)
        scheduler.run()
        self.assert_equal([0, 2, 4, 6, 8], results_list)

    def test_graphline_pattern(self):
        m4us.init()
        results_list1, results_list2 = [], []
        source = common.counter(5)
        ## pylint:disable=E1120
        filter_ = common.doubler()
        ## pylint:disable=E1111
        sink1 = common.accumulator(results_list1)
        sink2 = common.accumulator(results_list2)
        ## pylint:enable=E1111, E1120
        post_office = m4us.PostOffice()
        post_office.register(
            (source, 'outbox', sink1, 'inbox'),
            (source, 'signal', sink1, 'control'),
            (source, 'outbox', filter_, 'inbox'),
            (source, 'signal', filter_, 'control'),
            (filter_, 'outbox', sink2, 'inbox'),
            (filter_, 'signal', sink2, 'control'),
        )
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(source, filter_, sink1, sink2)
        scheduler.run()
        self.assert_equal([0, 1, 2, 3, 4], results_list1)
        self.assert_equal([0, 2, 4, 6, 8], results_list2)


#---Module initialization------------------------------------------------------

if __name__ == '__main__':
    unittest2.main()


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
