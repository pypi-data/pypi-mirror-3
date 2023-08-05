"""
===================
Gearman Task Server
===================
"""

__version__ = '0.1.1'

import time
import sys, traceback
import gearman
import signal

from multiprocessing import Process, Queue, cpu_count, active_children
from Queue import Empty


# Logging
import logging
log = logging.getLogger(__name__)

#
# A simple task function wrapper designed to exit gracefully and re-queue jobs
# when interrupted.
#

class Task(object):
    def __init__(self, name, task, verbose=False):
        self.name    = name
        self.task    = task
        self.verbose = verbose
    def __call__(self, worker, job):
        try:
            return self.task(worker, job)
        except Exception, e:
            if self.verbose:
                log.error('WORKER FAILED:  {0}, {1}\n{2}'.format(
                    self.name,
                    str(e),
                    traceback.format_exc()
                    ))
            # Disconnect so this job goes back into the queue
            worker.shutdown()
            # Continue with the exception
            raise

#
# Main server class
#

class GearmanTaskServer(object):

    def __init__(self,
            host_list, tasks, max_workers=None,
            id_prefix = None, GMWorker=None, sighandler=False, verbose=False
            ):
        self.host_list   = host_list
        self.tasks       = tasks
        self.max_workers = int(max_workers)
        self.worker      = GMWorker
        self.id_prefix   = id_prefix
        self.verbose     = verbose
        if not self.worker:
            self.worker = gearman.GearmanWorker
        # Signal Handler override?
        if sighandler:
            self.setup_sighandler()
        # Sanity check
        if self.max_workers < 1:
            try:
                self.max_workers = int(cpu_count())
            except:
                self.max_workers = 1

    def serve_forever(self):
        # Initialize a queue designed to track child processes that exit.
        doneq = Queue()
        # Keep track of how many clients we have created, so they can have unique IDs
        process_counter = 0
        # Loop
        workers = []
        try:
            while True:
                while len(workers) < self.max_workers:
                    process_counter += 1
                    client_id = None
                    if self.id_prefix:
                        client_id = '{0}{1}'.format(self.id_prefix, process_counter)
                    p = Process(target=_worker_process, args=(
                            self.tasks,
                            doneq,
                            self.host_list,
                            self.worker,
                            client_id,
                            self.verbose
                            ))
                    p.start()
                    workers.append(p)
                    if self.verbose:
                        log.info("Num workers:  {0} of {1}".format(len(workers), self.max_workers))
                # Use the queue as a poor man's wait/select against the first
                # child process to finish.  Add a timeout so we can repopulate
                # processes that terminate abnormally.
                try:
                    r = doneq.get(True, 5)
                except Empty:
                    r = None
                if r is not None:
                    if isinstance(r, gearman.errors.ServerUnavailable):
                        #: @todo non-blocking doneq.get() to clear it out of
                        #        similar errors? or maybe just reset doneq above
                        #        when len(workers)==0
                        if self.verbose:
                            log.info("Reconnecting.")
                        time.sleep(2)
                    elif r is True:
                        # Job exited normally.  Except this shouldn't actually happen.
                        log.info('Normal process exit (May actually be a problem)')
                # Give things a fraction of a second to catch up, then filter out
                # the finished process(es)
                time.sleep(0.1)
                workers = filter(lambda w: w in workers, active_children())
        except KeyboardInterrupt:
            log.error('EXIT.  RECEIVED INTERRUPT')

    def setup_sighandler(self):
        """
        Initialize our slight change to the signal handler setup

        Provided as a separate function so that users can opt in to this feature,
        or write their own.
        """
        signal.signal(signal.SIGINT,  _interrupt_handler)
        signal.signal(signal.SIGTERM, _interrupt_handler)

#
# Our own interrupt handler
#

def _interrupt_handler(signum, frame):
    """
    Python maps SIGINT to KeyboardInterrupt by default, but we need to
    catch SIGTERM as well, so we can give jobs as much of a chance as
    possible to alert the gearman server to requeue the job.
    """
    raise KeyboardInterrupt()

#
# Worker process/function
#

def _worker_process(tasks, doneq, host_list, worker_class=None, client_id=None, verbose=False):
    try:
        if not worker_class:
            worker_class = gearman.GearmanWorker
        try:
            # Connect
            gm_worker = worker_class(host_list = host_list)
            if client_id:
                gm_worker.set_client_id(client_id)
            # Load the tasks
            for task in tasks:
                if verbose:
                    log.info("Registering {0} task {1}".format(client_id, task.name))
                if isinstance(task, dict):
                    gm_worker.register_task(task['name'], task['task'])
                elif isinstance(task, list) or isinstance(task, tuple):
                    gm_worker.register_task(task[0], task[1])
                else:
                    gm_worker.register_task(task.name, task)
            # Enter the work loop
            gm_worker.work()
        except gearman.errors.ServerUnavailable, e:
            doneq.put(e)
            return
        # Really should never touch this code but it's here just in case.
        doneq.put(True)
    except KeyboardInterrupt:
        # Prevent this child process from printing a traceback
        pass
