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


"""Common testing coroutines and components m4us.core integration tests."""


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
## pylint: disable=E0611
from zope import interface
## pylint: enable=E0611

#---  Project imports
import m4us.api as m4us


#---Globals--------------------------------------------------------------------


#---Functions------------------------------------------------------------------

@m4us.producer
def counter(max_count):
    for number in xrange(max_count):
        yield number


@m4us.filter_
def doubler(message):
    return message * 2


@m4us.sink
def accumulator(message, results_list):
    results_list.append(message)


#---Classes--------------------------------------------------------------------

class Counter(m4us.Component):

    interface.implements(m4us.INotLazy)
    interface.classProvides(m4us.ICoroutineFactory)

    def __init__(self, max_count, **kwargs):
        m4us.Component.__init__(self, max_count=max_count, **kwargs)

    def _main(self):
        yield
        for number in xrange(self.max_count):
            yield 'outbox', number
        yield 'signal', m4us.ProducerFinished()


class Doubler(m4us.Component):

    interface.classProvides(m4us.ICoroutineFactory)

    def _main(self):
        inbox, message = (yield)
        while True:
            if m4us.is_shutdown(inbox, message):
                yield 'signal', message
                break
            inbox, message = (yield 'outbox', message * 2)


class Accumulator(m4us.Component):

    interface.classProvides(m4us.ICoroutineFactory)

    def __init__(self, **kwargs):
        self.results_list = []
        m4us.Component.__init__(self, **kwargs)

    def _main(self):
        while True:
            inbox, message = (yield)
            if m4us.is_shutdown(inbox, message):
                yield 'signal', message
                break
            self.results_list.append(message)


#---Module initialization------------------------------------------------------


#---Late Imports---------------------------------------------------------------


#---Late Globals---------------------------------------------------------------


#---Late Functions-------------------------------------------------------------


#---Late Classes---------------------------------------------------------------


#---Late Module initialization-------------------------------------------------
