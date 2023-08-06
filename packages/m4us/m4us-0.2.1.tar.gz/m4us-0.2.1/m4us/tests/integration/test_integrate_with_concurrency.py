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


"""Integration tests for m4us.concurrency."""


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

class TestConcurrencyIntegration(support.TestCase):

    def test_with_coroutines(self):
        m4us.init()
        results_list = []
        pipeline = m4us.Pipeline(
          m4us.ThreadedCoroutine(common.counter(5)),
          ## pylint:disable=E1120
          m4us.ThreadedCoroutine(common.doubler()),
          m4us.ThreadedCoroutine(common.accumulator(results_list)),
          ## pylint:enable=E1120
        )
        post_office = m4us.PostOffice()
        post_office.register(*pipeline.links)
        scheduler = m4us.Scheduler(post_office)
        scheduler.register(*pipeline.coroutines)
        scheduler.run()
        self.assert_equal([0, 2, 4, 6, 8], results_list)

    def test_with_components(self):
        m4us.init()
        sink = common.Accumulator()
        pipeline = m4us.Pipeline(
          m4us.ThreadedCoroutine(common.Counter(5)),
          m4us.ThreadedCoroutine(common.Doubler()),
          m4us.ThreadedCoroutine(sink),
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
