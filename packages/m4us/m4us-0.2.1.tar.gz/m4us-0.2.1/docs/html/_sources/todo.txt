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

.. _todo:

To Do Items Index
=================

General To Do Items
-------------------

- Change @coroutine so that only Python coroutines that use it are considered
  ICoroutine and not all Python coroutines.
- Add required keyword arguments for exceptions and tests to check for them.
- Remove extra keyword argument support from messages and components.
- Add specialized Components that match filter_from_callable(),
  producer_from_iterable() and sink_from_callable().
- Make IPostOffice and IScheduler directly accept containers without needing
  to pass in only .coroutines or .links.
- Change IContainer to IGrouping and containers to groupings.  They don't
  actually *contain* anyting.  They just group coroutines together.
- Create explicit Link and Message objects, interfaces, and adaptation to
  tuples.
- Create a general "provides or adapts to" interface function in utils and use
  is.
- See about spliting scheduling and message delivery out into seperate classes.
- Remove the api modules and just import the APIs in the pacakge __init__.py
  files.
- M4USException should also have a __unicode__ mehtod and __str__ should encode
  the exception message into bytes.
- Add convenience components that dispatch to a single method for each message,
  a different method per message type and a different method per inbox.
- Move the IScheduler.run(cycles) parameter to ISheduler.cycle(cycles=1).  This
  is more consistent to each method having a single purpose.
- Test the project under Python 2.7.
- Make the project work under Python 3.1.
- Expand documentation.
- Add doctests as working examples to all docstrings.
- Remove superfluous "See Also", and make object references short (i.e. use ~)
- See about running cheesecake and making it happy.
- Set up a mailing list for feedback. (librelist.org?, not Google groups)
- Setup Hudson somewhere for continuous integration.
- Refactor all code as per the book Beautiful Code.
- Add logging support to all existing objects.
- Add a logging/provenance coroutine that goes in front of other coroutines and
  sends logging messages out on a different mailbox.
- Add a multi-process coroutine adapter like ThreadedCoroutine.
- Add file processing coroutines.
- Add an external interface to manually send messages into a running system as
  if one were just calling a function/method.
- Add an adapter so that  Kamaelia components can be used directly.
- Add a AMQP coroutine adapter.
- Add a 0MQ coroutine adapter.
- Add an eventlet-bases scheduler.
- Add a Twisted-baded scheduler.
- See about VisTrails integration.
- Add network stream processing coroutines
- Add support for network services including HTTP, etc.
- Add support for running WSGI apps.
- Add more Kamaelia-inspired constructs.
- Split out the Paver tasks into a seperate generic package.
- Split out the test infrastructure into a seperate generic package.
- Maybe split out the completely generic utility code into it's own seperate
- package.  (memoize, Pep8itfying code, etc.)
- Submit dependency fixes, workarounds and enhancements to upstream projects to
  help improve them. (Paver virtualenv, Unittest2 assert_not_raises, & pep8ify,
  etc.)

Code and Documentation To Do Items
----------------------------------

.. todolist::
