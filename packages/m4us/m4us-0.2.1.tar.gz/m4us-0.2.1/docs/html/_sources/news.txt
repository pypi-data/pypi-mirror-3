.. This file is part of Message For You Sir (m4us).
.. Copyright © 2010 Krys Lawrence
..
.. Message For You Sir is free software: you can redistribute it and/or modify
.. it under the terms of the GNU Affero General Public License as published by
.. the Free Software Foundation, either version 3 of the License, or (at your
.. option) any later version.
..
.. Message For You Sir is distributed in the hope that it will be useful, but
.. WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
.. or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public
.. License for more details.
..
.. You should have received a copy of the GNU Affero General Public License
.. along with Message For You Sir.  If not, see <http://www.gnu.org/licenses/>.

.. include:: ../../NEWS

.. |m4us.tests.run()| replace:: :func:`m4us.tests.run`
.. |python -m m4us.tests.__init__| replace::
    :command:`python -m m4us.tests.__init__`
.. |coroutine()| replace:: :func:`~m4us.core.coroutines.coroutine`
.. |backplane()| replace:: :func:`~m4us.backplanes.backplane`
.. |publish_to()| replace:: :func:`~m4us.backplanes.publish_to`
.. |init()| replace:: :func:`~m4us.core.coroutines.init`
.. |IPostOffice| replace:: :class:`~m4us.core.interfaces.IPostOffice`
.. |IPostOffice.register()| replace::
    :meth:`~m4us.core.interfaces.IPostOffice.register`
.. |IPostOffice.unregister()| replace::
    :meth:`~m4us.core.interfaces.IPostOffice.unregister`
.. |IScheduler| replace:: :class:`~m4us.core.interfaces.IScheduler`
.. |IScheduler.register()| replace::
    :meth:`~m4us.core.interfaces.IScheduler.register`
.. |IScheduler.unregister()| replace::
    :meth:`~m4us.core.interfaces.IScheduler.unregister`
.. |IContainer| replace:: :class:`~m4us.core.interfaces.IContainer`
.. |IContainer.coroutines| replace::
    :attr:`~m4us.core.interfaces.IContainer.coroutines`
.. |IContainer.links| replace:: :attr:`~m4us.core.interfaces.IContainer.links`
.. |filter_from_callable()| replace::
    :func:`~m4us.core.coroutines.filter_from_callable`
.. |producer_from_iterable()| replace::
    :func:`~m4us.core.coroutines.producer_from_iterable`
.. |sink_from_callable()| replace::
    :func:`~m4us.core.coroutines.sink_from_callable`
.. |filter_()| replace:: :func:`~m4us.core.coroutines.filter_`
.. |producer()| replace:: :func:`~m4us.core.coroutines.producer`
.. |sink()| replace:: :func:`~m4us.core.coroutines.sink`
.. |example.py| replace:: :ref:`example.py <example.py>`
.. |paver lint| replace:: :command:`paver lint`
.. |paver tests_lint| replace:: :command:`paver tests_lint`
.. |paver check| replace:: :command:`paver check`

.. _decorator: http://pypi.python.org/pypi/decorator
.. _nose: http://pypi.python.org/pypi/nose
.. _strait: http://pypi.python.org/pypi/strait
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.event: http://pypi.python.org/pypi/zope.event
.. _python: http://python.org/
.. _unittest2: http://pypi.python.org/pypi/unittest2
.. _mock: http://pypi.python.org/pypi/mock
