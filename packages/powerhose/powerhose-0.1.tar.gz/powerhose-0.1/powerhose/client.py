import zmq
import threading
from Queue import Queue
import traceback
import sys

from powerhose.exc import TimeoutError
from powerhose.job import Job
from powerhose.util import send, recv, DEFAULT_FRONTEND, logger


class Client(object):
    """Class to call a Powerhose cluster.

    Options:

    - **frontend**: ZMQ socket to call.
    - **timeout**: maximum allowed time for a job to run.
      Defaults to 5s.
    """
    def __init__(self, frontend=DEFAULT_FRONTEND, timeout=5.):
        self.ctx = zmq.Context(io_threads=2)
        self.master = self.ctx.socket(zmq.REQ)
        self.master.connect(frontend)
        logger.debug('Client connected to %s' % frontend)
        self.poller = zmq.Poller()
        self.poller.register(self.master, zmq.POLLIN)
        self.timeout = timeout * 1000
        self.lock = threading.Lock()

    def execute(self, job, timeout=None):
        """Runs the job

        Options:

        - **job**: Job to be performed. Can be a :class:`Job`
          instance or a string. If it's a string a :class:`Job` instance
          will be automatically created out of it.
        - **timeout**: maximum allowed time for a job to run.
          If not provided, uses the one defined in the constructor.

        If the job fails after the timeout, raises a :class:`TimeoutError`.

        This method is thread-safe and uses a lock. If you need to execute a
        lot of jobs simultaneously on a broker, use the :class:`Pool` class.

        """
        if isinstance(job, str):
            job = Job(job)

        if timeout is None:
            timeout = self.timeout

        with self.lock:
            send(self.master, job.serialize())
            socks = dict(self.poller.poll(timeout))

        if socks.get(self.master) == zmq.POLLIN:
            return recv(self.master)

        raise TimeoutError()


class Pool(object):
    """The pool class manage several :class:`CLient` instances
    and publish the same interface,

    Options:

    - **size**: size of the pool. Defaults to 10.
    - **frontend**: ZMQ socket to call.
    - **timeout**: maximum allowed time for a job to run.
      Defaults to 5s.
    """
    def __init__(self, size=10, frontend=DEFAULT_FRONTEND, timeout=5.):
        self._connectors = Queue()
        self.frontend = frontend
        self.timeout = timeout
        for i in range(size):
            self._connectors.put(Client(frontend, timeout))

    def execute(self, job, timeout=None):
        connector = self._connectors.get(timeout=timeout)
        try:
            return connector.execute(job, timeout)
        except Exception, e:
            # logged, connector replaced.
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc = traceback.format_tb(exc_traceback)
            exc.insert(0, str(e))
            logger.error('\n'.join(exc))
            try:
                connector.ctx.destroy(0)
            except Exception:
                pass
            self._connectors.put(Client(self.frontend, self.timeout))
        finally:
            self._connectors.put(connector)
