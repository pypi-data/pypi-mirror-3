"""
lava.celery.tasks
=================

Task definitions imported by celeryd when configured to use lava.celery.config
"""

import sys

from celery.messaging import establish_connection
from celery.task import task
from kombu.compat import Publisher
from lava.tool.main import LavaDispatcher

from lava.celery.queues import StreamExchange


__all__ = ["run_command"]


class CloudifiedDispatcher(LavaDispatcher):
    """
    Dispatcher suitable to run commands and stream their output back to the
    originator via kombu.
    """

    def __init__(self, publisher):
        super(CloudifiedDispatcher, self).__init__()
        self.publisher = publisher

    def say(self, command, message, *args, **kwargs):
        text = message.format(*args, **kwargs)
        self.publisher.send({
            'command': command.get_name(),
            'say': text
        })


class WriteProxy(object):
    """
    Simple proxy for File-like objects that redirects write() to a callback
    """

    def __init__(self, stream, write_cb):
        self._stream = stream
        self._write_cb = write_cb

    def write(self, data):
        self._write_cb(data)

    def __getattr__(self, attr):
        return getattr(self._stream, attr)


@task(acks_late=True, ignore_result=True)
def run_command(queue_name, args):
    """
    Run a lava-tool command with the specified arguments
    """
    connection = establish_connection()
    channel = connection.channel()
    publisher = Publisher(
        connection=channel,
        exchange=StreamExchange,
        routing_key=queue_name,
        exchange_type="direct")
    orig_stdout = sys.stdout
    sys.stdout = WriteProxy(sys.stdout, lambda data: publisher.send({"stdout": data}))
    orig_stderr = sys.stderr
    sys.stderr = WriteProxy(sys.stderr, lambda data: publisher.send({"stderr": data}))
    retval = None
    try:
        retval = CloudifiedDispatcher(publisher).dispatch(args)
    except SystemExit as exc:
        retval = exc.code
    finally:
        publisher.send({'done': retval})
        publisher.close()
        connection.close()
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr
