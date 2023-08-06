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

Glossary
========

.. glossary::
    :sorted:

    Adapter
    Adapters
      ..

        "In computer programming, the adapter design pattern (often referred
        to as the wrapper pattern or simply a wrapper) translates one interface
        for a class into a compatible interface. An adapter allows classes to
        work together that normally could not because of incompatible
        interfaces, by providing its interface to clients while using the
        original interface. The adapter translates calls to its interface into
        calls to the original interface, and the amount of code necessary to do
        this is typically small. The adapter is also responsible for
        transforming data into appropriate forms."

        —Wikipedia_ page on the `adapter pattern`_

      In this project, this pattern has been formalized by the use of the
      zope.interface_ and zope.component_ packages.  zope.interface_ prvides a
      method to formally define interfaces independent of their
      implementations, and zope.component_ facilitates the creation and
      registration of adapters when they are necessary.

      You can find more information on the Zope Component Architecture and it's
      adapter system by reading `A Comprehensive Guide to Zope Component
      Architecture`_ by Baiju M, in particular `chapter 4`_, as well as in the
      documentation for the zope.interface_ and zope.component_ packages.  For
      more general information about adapters, see the Wikipedia_ page on the
      `adapter pattern`_.

      .. _Wikipedia: http://wikipedia.org/
      .. _adapter pattern: http://en.wikipedia.org/wiki/Adapter_pattern
      .. _zope.interface: http://pypi.python.org/pypi/zope.interface
      .. _zope.component: http://pypi.python.org/pypi/zope.component
      .. _A Comprehensive Guide to Zope Component Architecture:
        http://www.muthukadan.net/docs/zca.html
      .. _chapter 4: http://www.muthukadan.net/docs/zca.html#adapters

    Backplane
    Backplanes
      .. todo:: Document term Backplane

    Callable
    Callables
      In Python_, A callable is a generic term for any object that can be
      called.  This is usually a function or a method, but can be any object
      that defines a :meth:`!__call__` method.  For more information see the
      Python_ documentation on `Emulating callable objects`_

      .. _Emulating callable objects:
        http://docs.python.org/reference/datamodel.html#emulating-callable-objects

    Component
    Components
      .. todo:: Document term Component

    Concurrent
      .. todo:: Document term Concurrent

    Consumer
      .. todo:: Document term Consumer

    Consumers
      See `Consumer`

    Container
      .. todo:: Document term Container

    Coroutine
    Coroutines
      ..

        "A coroutine is a generalization of the subroutine. Forget for a moment
        everything you've been taught about calling functions, and stacks,
        etc... Think back to BASIC, and the evil GOTO statement. Imagine a more
        powerful GOTO that could jump back and forth between functions, passing
        arguments, and you begin to get the idea."

        "Coroutines are a bit of ancient forgotten computer-science lore;
        stamped out of the collective memory by the hegemony of C. But they are
        useful in a wide variety of situations that can only be clumsily solved
        using 'standard' tools like threads and processes."

        —`Coroutines In Python`_

      Coroutines in Python_ are described in :PEP:`342`.  There is an excellent
      presentation on Python_ coroutines titled `A Curious Course on Coroutines
      and Concurrency`_ by `David Beazley`_.  For information on coroutines in
      general, see the `Wikipedia page on coroutines`_.

      .. _Coroutines In Python: http://www.nightmare.com/~rushing/copython/
      .. _Python: http://python.org
      .. _A Curious Course on Coroutines and Concurrency:
        http://www.dabeaz.com/coroutines/
      .. _David Beazley: http://www.dabeaz.com/
      .. _Wikipedia page on coroutines: http://en.wikipedia.org/wiki/Coroutine

    Factory
      .. todo:: Document term Factory

    Filter
    Filters
      .. todo:: Document term Filter

    Framework
      For this project, a framework is simply defined as something that calls
      your code, rather than your code calling it.  (As opposed to a
      `library`.)  For general information on the concept if a framework in
      software, see the `Wikipedia page on software frameworks`_.

      .. _Wikipedia page on software frameworks:
        http://en.wikipedia.org/wiki/Software_framework

    Generator
    Generators
      ..

        "A generator is, simply put, a function which can stop whatever it is
        doing at an arbitrary point in its body, return a value back to the
        caller, and, later on, resume from the point it had 'frozen' and
        merrily proceed as if nothing had happened."

        —`Python Generator Tricks`_

      Generators in Python_ are described in :PEP:`255`.  There is an excellent
      presentation on Python_ generators titled `Generator Tricks for Systems
      Programmers`_ by `David Beazley`_.  For information on generators in
      general, see the `Wikipedia page on generators`_.

      .. _Python Generator Tricks: http://linuxgazette.net/100/pramode.html
      .. _Generator Tricks for Systems Programmers:
        http://www.dabeaz.com/generators/
      .. _Wikipedia page on generators:
        http://en.wikipedia.org/wiki/Generator_%28computer_science%29

    Idempotent
      .. todo:: Document term idempotent

    Inbox
    Inboxes
      .. todo:: Document term Inbox

    Interface
    interfaces
      .. todo:: Document term Interface

    Lazy
      .. todo:: Document term Lazy

    Library
      For this project, a library is simply defined as packaged code that you
      call in your program.  (As opposed to a `framework` that calls your code
      for you.)  For general information on the concept if a library in
      software, see the `Wikipedia page on libraries`_.

      .. _Wikipedia page on libraries:
        http://en.wikipedia.org/wiki/Library_%28computing%29

    Link
    Links
      .. todo:: Document term Link

    Mailbox
    Mailboxes
      .. todo:: Document term Mailbox

    Message
    Messages
      .. todo:: Document term Message

    Outbox
    Outboxes
      .. todo:: Document term Outbox


    Pipeline
    Pipelines
      .. todo:: Document term Pipeline

    Post Office
    Post Offices
      .. todo:: Document term Post Office

    Producer
    Producers
      For this project, a producer is a coroutine that produces messages to be
      consumed, but does not consume any messages itself (aside from shutdown
      messages).  For example, reading lines from a files and send them out one
      at a time.  For general information on the concept of a producer, see the
      `Wikipedia page on the Producer-consumer problem`_.

      .. _Wikipedia page on the Producer-consumer problem:
        http://en.wikipedia.org/wiki/Producer-consumer_problem

    Publisher
    Publishers
      .. todo:: Document term Publisher

    Scheduler
    Schedulers
      .. todo:: Document term Scheduler

    Sink
      .. todo:: Document term Sink

    Source
      .. todo:: Document term Source

    Subscriber
    Subscribers
      .. todo:: Document term Subscriber
