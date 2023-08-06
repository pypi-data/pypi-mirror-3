# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
import os
import errno
import time
import sys
import traceback
import argparse
import logging
import threading
import Queue
import contextlib
import random

import zmq

from powerhose import util
from powerhose.util import (logger, set_logger, DEFAULT_BACKEND,
                            DEFAULT_HEARTBEAT)
from powerhose.job import Job
from powerhose.util import resolve_name, decode_params, timed, dump_stacks
from powerhose.heartbeat import Stethoscope
from powerhose.client import DEFAULT_TIMEOUT_MOVF

from zmq.eventloop import ioloop, zmqstream


DEFAULT_MAX_AGE = -1
DEFAULT_MAX_AGE_DELTA = 0


class ExecutionTimer(threading.Thread):

    def __init__(self, timeout=DEFAULT_TIMEOUT_MOVF, interval=.1):
        logger.debug('Initializing the execution timer. timeout is %.2f' \
                % timeout)
        threading.Thread.__init__(self)
        self.armed = self.running = False
        self.timeout = timeout
        self.daemon = True

        # creating a queue for I/O with the worker
        self.queue = Queue.Queue()
        self.interval = interval
        self.timed_out = self.working = False
        self.last_dump = None

    @contextlib.contextmanager
    def run_job(self):
        self.job_starts()
        try:
            yield
        finally:
            self.job_ends()

    def job_starts(self):
        if self.working:
            raise ValueError("The worker is already busy -- call job_ends")
        self.working = True
        self.timed_out = False
        self.queue.put('STARTING')

    def job_ends(self):
        if not self.working:
            raise ValueError("The worker is not busy -- call job_starts")
        self.queue.put('DONE')
        self.working = self.armed = False

    def run(self):
        self.running = True

        while self.running:
            # arming, so waiting for ever
            self.queue.get()
            self.armed = True

            # now waiting for the second call, which means
            # the worker has done the work.
            #
            # This time we time out
            try:
                self.queue.get(timeout=self.timeout)
            except Queue.Empty:
                # too late, we want to log the stack
                self.last_dump = dump_stacks()
                self.timed_out = True
            finally:
                self.armed = False

    def stop(self):
        self.running = False
        if not self.armed:
            self.queue.put('STARTING')
        self.queue.put('DONE')
        if self.isAlive():
            self.join()


class Worker(object):
    """Class that links a callable to a broker.

    Options:

    - **target**: The Python callable that will be called when the broker
      send a job.
    - **backend**: The ZMQ socket to connect to the broker.
    - **heartbeat**: The ZMQ socket to perform PINGs on the broker to make
      sure it's still alive.
    - **ping_delay**: the delay in seconds betweem two pings.
    - **ping_retries**: the number of attempts to ping the broker before
      quitting.
    - **params** a dict containing the params to set for this worker.
    - **timeout** the maximum time allowed before the thread stacks is dump
      and the job result not sent back.
    - **max_age**: maximum age for a worker in seconds. After that delay,
      the worker will simply quit. When set to -1, never quits.
      Defaults to -1.
    - **max_age_delta**: maximum value in seconds added to max age.
      The Worker will quit after *max_age + random(0, max_age_delta)*
      This is done to avoid having all workers quit at the same instant.
      Defaults to 0. The value must be an integer.
    """
    def __init__(self, target, backend=DEFAULT_BACKEND,
                 heartbeat=DEFAULT_HEARTBEAT, ping_delay=1., ping_retries=3,
                 params=None, timeout=DEFAULT_TIMEOUT_MOVF,
                 max_age=DEFAULT_MAX_AGE, max_age_delta=DEFAULT_MAX_AGE_DELTA):
        logger.debug('Initializing the worker.')
        self.ctx = zmq.Context()
        self.backend = backend
        self._backend = self.ctx.socket(zmq.REP)
        self._backend.connect(self.backend)
        self.target = target
        self.running = False
        self.loop = ioloop.IOLoop()
        self._backstream = zmqstream.ZMQStream(self._backend, self.loop)
        self._backstream.on_recv(self._handle_recv_back)
        self.ping = Stethoscope(heartbeat, onbeatlost=self.lost,
                                delay=ping_delay, retries=ping_retries)
        self.debug = logger.isEnabledFor(logging.DEBUG)
        self.params = params
        self.pid = os.getpid()
        self.timer = ExecutionTimer(timeout=timeout)
        self.max_age = max_age
        self.max_age_delta = max_age_delta
        self.delayed_exit = None
        self.lock = threading.RLock()

    def _handle_recv_back(self, msg):
        # do the job and send the result
        if self.debug:
            logger.debug('Job received')
            target = timed()(self.target)
        else:
            target = self.target

        duration = -1

        # results are sent with a PID:OK: or a PID:ERROR prefix
        try:
            with self.timer.run_job():
                res = target(Job.load_from_string(msg[0]))

            # did we timout ?
            if self.timer.timed_out:
                # let's dump the last
                for line in self.timer.last_dump:
                    logger.error(line)

            if self.debug:
                duration, res = res
            res = '%d:OK:%s' % (self.pid, res)
        except Exception, e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            exc = traceback.format_tb(exc_traceback)
            exc.insert(0, str(e))
            res = '%d:ERROR:%s' % (self.pid, '\n'.join(exc))
            logger.error(res)

        if self.timer.timed_out:
            # let's not send back anything, we know the client
            # is gone anyway
            return

        if self.debug:
            logger.debug('Duration - %.6f' % duration)

        try:
            self._backstream.send(res)
        except Exception:
            logging.error("Could not send back the result", exc_info=True)

    def lost(self):
        logger.info('Master lost ! Quitting..')
        self.running = False
        self.loop.stop()
        return True

    def stop(self):
        """Stops the worker.
        """
        logger.debug('Stopping the worker')
        self.running = False
        try:
            self._backstream.flush()
        except zmq.core.error.ZMQError:
            pass
        self.loop.stop()
        self.ping.stop()
        self.timer.stop()
        time.sleep(.1)
        self.ctx.destroy(0)
        logger.debug('Worker is stopped')

    def start(self):
        """Starts the worker
        """
        util.PARAMS = self.params

        logger.debug('Starting the worker loop')

        # running the pinger
        self.ping.start()
        self.timer.start()
        self.running = True

        # arming the exit callback
        if self.max_age != -1:
            if self.max_age_delta > 0:
                delta = random.randint(0, self.max_age_delta)
            else:
                delta = 0

            cb_time = self.max_age + delta
            self.delayed_exit = ioloop.DelayedCallback(self.stop,
                                                       cb_time * 1000,
                                                       io_loop=self.loop)
            self.delayed_exit.start()

        while self.running:
            try:
                self.loop.start()
            except zmq.ZMQError as e:
                logger.debug(str(e))

                if e.errno == errno.EINTR:
                    continue
                elif e.errno == zmq.ETERM:
                    break
                else:
                    logger.debug("got an unexpected error %s (%s)", str(e),
                                 e.errno)
                    raise
            else:
                break

        logger.debug('Worker loop over')


def main(args=sys.argv):

    parser = argparse.ArgumentParser(description='Run some watchers.')

    parser.add_argument('--backend', dest='backend',
                        default=DEFAULT_BACKEND,
                        help="ZMQ socket to the broker.")

    parser.add_argument('target', help="Fully qualified name of the callable.")

    parser.add_argument('--debug', action='store_true', default=False,
                        help="Debug mode")

    parser.add_argument('--logfile', dest='logfile', default='stdout',
                        help="File to log in to.")

    parser.add_argument('--heartbeat', dest='heartbeat',
                        default=DEFAULT_HEARTBEAT,
                        help="ZMQ socket for the heartbeat.")

    parser.add_argument('--params', dest='params', default=None,
                        help='The parameters to be used in the worker.')

    parser.add_argument('--timeout', dest='timeout', type=float,
                        default=DEFAULT_TIMEOUT_MOVF,
                        help=('The maximum time allowed before the thread '
                              'stacks is dump and the job result not sent '
                              'back.'))

    parser.add_argument('--max-age', dest='max_age', type=float,
                        default=DEFAULT_MAX_AGE,
                        help=('The maximum age for a worker in seconds. '
                              'After that delay, the worker will simply quit. '
                              'When set to -1, never quits.'))

    parser.add_argument('--max-age-delta', dest='max_age_delta', type=int,
                        default=DEFAULT_MAX_AGE_DELTA,
                        help='The maximum value in seconds added to max_age')

    args = parser.parse_args()
    set_logger(args.debug, logfile=args.logfile)
    sys.path.insert(0, os.getcwd())  # XXX
    target = resolve_name(args.target)
    if args.params is None:
        params = {}
    else:
        params = decode_params(args.params)

    logger.info('Worker registers at %s' % args.backend)
    logger.info('The heartbeat socket is at %r' % args.heartbeat)
    worker = Worker(target, backend=args.backend, heartbeat=args.heartbeat,
                    params=params, timeout=args.timeout, max_age=args.max_age,
                    max_age_delta=args.max_age_delta)

    try:
        worker.start()
    except KeyboardInterrupt:
        return 1
    finally:
        worker.stop()

    return 0


if __name__ == '__main__':
    main()
