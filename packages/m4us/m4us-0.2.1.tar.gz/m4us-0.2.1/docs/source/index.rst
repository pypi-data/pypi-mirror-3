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

####################
Message For You Sir!
####################

:Date: |today|
:Version: |release|
:Status: 3 - Alpha
:Author: Krys Lawrence
:Contact: m4us at krys ca
:Copyright: 2009-2010, Krys Lawrence
:License: `GNU Affero General Public License version 3`_ (AGPLv3+)

*******************
Project Information
*******************

.. include:: ../../README
   :start-after: .. about
   :end-before: .. features

.. include:: ../../README
   :start-after: .. features
   :end-before: .. status

.. include:: ../../README
   :start-after: .. status
   :end-before: .. installation

.. include:: ../../README
   :start-after: .. installation
   :end-before: .. basic_usage

.. include:: ../../README
   :start-after: .. basic_usage
   :end-before: .. documentation_and_support

.. include:: ../../README
   :start-after: .. documentation_and_support
   :end-before: .. contributing

.. include:: ../../README
   :start-after: .. contributing
   :end-before: .. licence

.. include:: ../../README
   :start-after: .. licence
   :end-before: .. credits

.. include:: ../../README
   :start-after: .. credits
   :end-before: .. end

*************
Documentation
*************

.. toctree::
   :maxdepth: 2

   example
   licence
   news
   api/index
   appendix_a

******************
Indices and Tables
******************

* :doc:`glossary`
* :ref:`genindex`
* :ref:`modindex`
* :ref:`todo`
* :ref:`search`

.. toctree::
   :hidden:

   glossary
   todo

.. These are hacks get around the fact that PyPI does not properly render links
.. in substitutions.
.. |(in docs/example.py)| replace:: \ \
.. |(in docs/source/todo.rst)| replace:: \ \
.. |(in LICENCE)| replace:: \ \
.. _A Simple Example: example.html
.. _To Do Items Index: todo.html
.. _Licensing Information: licence.html

.. include:: ../../README
   :start-after: .. links
