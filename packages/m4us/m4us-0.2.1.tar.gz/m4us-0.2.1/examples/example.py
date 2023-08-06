# -*- coding: utf-8 -*-
# docs/example.py

"""Trivial and silly example of m4us."""


from __future__ import print_function
from __future__ import unicode_literals
import io

from zope import interface
import m4us.api as m4us


TEXT = """\
Line 1
Line 2
Line 3
"""


def main():
    """Print the repr() of each line of TEXT, followed by a line count."""
    m4us.init()
    source = lines_producer(io.StringIO(TEXT, 'utf-8'))
    filter_ = Counter()
    sink = repr_consumer()
    pipeline = m4us.Pipeline(source, filter_, sink)
    post_office = m4us.PostOffice()
    scheduler = m4us.Scheduler(post_office)
    post_office.register(*pipeline.links)
    scheduler.register(*pipeline.coroutines)
    scheduler.run()
    print('Line count:', filter_.count)


@m4us.producer
def lines_producer(file_):
    """Emit lines from a file as messages."""
    for line in file_:
        yield line.strip()


@m4us.sink
def repr_consumer(message):
    """Print to stdout."""
    print(repr(message))


class Counter(m4us.Component):

    """Count messages and pass them through."""

    interface.classProvides(m4us.ICoroutineFactory)

    def _main(self):
        """Main loop for this component."""
        self.count = 0
        inbox, message = (yield)
        while True:
            if m4us.is_shutdown(inbox, message):
                yield 'signal', message
                break
            self.count += 1
            inbox, message = (yield 'outbox', message)


if __name__ == '__main__':
    main()
