.. This file is part of Message For You Sir (m4us).
.. Copyright © 2009-2012 Krys Lawrence
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

.. |m4us.tests.run()| replace:: :func:`.run`
.. |python -m m4us.tests.__init__| replace::
    :command:`python -m m4us.tests.__init__`
.. |coroutine()| replace:: :func:`.coroutine`
.. |backplane()| replace:: :func:`.backplane`
.. |publish_to()| replace:: :func:.publish_to`
.. |init()| replace:: :func:`.init`
.. |IPostOffice| replace:: :class:`~m4us.core.interfaces.IPostOffice`
.. |IPostOffice.register()| replace:: :meth:`.IPostOffice.register`
.. |IPostOffice.unregister()| replace:: :meth:`.IPostOffice.unregister`
.. |IScheduler| replace:: :class:`~m4us.core.interfaces.IScheduler`
.. |IScheduler.register()| replace:: :meth:`.IScheduler.register`
.. |IScheduler.unregister()| replace:: :meth:`.IScheduler.unregister`
.. |IContainer| replace:: :class:`~m4us.core.interfaces.IContainer`
.. |IContainer.coroutines| replace:: :attr:`.IContainer.coroutines`
.. |IContainer.links| replace:: :attr:`.IContainer.links`
.. |filter_from_callable()| replace:: :func:`.filter_from_callable`
.. |producer_from_iterable()| replace:: :func:`.producer_from_iterable`
.. |sink_from_callable()| replace:: :func:`.sink_from_callable`
.. |filter_()| replace:: :func:`.filter_`
.. |producer()| replace:: :func:`.producer`
.. |sink()| replace:: :func:`.sink`
.. |example.py| replace:: :ref:`example.py <example.py>`
.. |setup.py| replace:: :file:`setup.py`
.. |paver pep8| replace:: :command:`paver pep8`
.. |paver release| replace:: :command:`paver release`
.. |paver pdf| replace:: :command:`paver pdf`
.. |paver text| replace:: :command:`paver text`
.. |paver docs| replace:: :command:`paver docs`
.. |paver flakes| replace:: :command:`paver flakes`
.. |paver sdist| replace:: :command:`paver sdist`
.. |paver html| replace:: :command:`paver html`
.. |paver lint| replace:: :command:`paver lint`
.. |paver tests_lint| replace:: :command:`paver tests_lint`
.. |paver check| replace:: :command:`paver check`

.. _zope.interface: http://pypi.python.org/pypi/zope.interface
.. _mock: http://pypi.python.org/pypi/mock
.. _distribute: http://pypi.python.org/pypi/distribute
.. _pep8: http://pypi.python.org/pypi/pep8
.. _pyflakes: http://pypi.python.org/pypi/pyflakes
.. _ipython:  http://pypi.python.org/pypi/ipython
.. _virtualenv: http://pypi.python.org/pypi/virtualenv
.. _coverage: http://pypi.python.org/pypi/coverage
.. _pylint: http://pypi.python.org/pypi/pylint
.. _sphinx: http://pypi.python.org/pypi/sphinx
.. _docutils: http://pypi.python.org/pypi/docutils
.. _jinja2: http://pypi.python.org/pypi/jinja2
.. _pygments: http://pypi.python.org/pypi/pygments
.. _sphinxcontrib-paverutils:
  http://pypi.python.org/pypi/sphinxcontrib-paverutils
.. _Paver: http://pypi.python.org/pypi/Paver
.. _clonedigger: : http://pypi.python.org/pypi/clonedigger
.. _forked version: https://bitbucket.org/krys/repoze.sphinx.autointerface_fork
.. _repoze.sphinx.autointerface:
  http://pypi.python.org/pypi/repoze.sphinx.autointerface
.. _flake8: http://pypi.python.org/pypi/flake8
.. _decorator: http://pypi.python.org/pypi/decorator
.. _nose: http://pypi.python.org/pypi/nose
.. _strait: http://pypi.python.org/pypi/strait
.. _zope.component: http://pypi.python.org/pypi/zope.component
.. _zope.event: http://pypi.python.org/pypi/zope.event
.. _python: http://python.org/
.. _unittest2: http://pypi.python.org/pypi/unittest2
.. _everyapp.bootstrap: http://pypi.python.org/pypi/everyapp.bootstrap
