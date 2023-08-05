#!/usr/bin/env python

# Stuff
from multiprocessing   import freeze_support
from gmtasks.jsonclass import GearmanWorker
from gmtasks           import GearmanTaskServer, Task

if __name__ == '__main__':
    # Need this on the off chance it'll ever run in Windows
    freeze_support()
    # Info
    guid = 'job.{0}.'.format(get_guid('w'))
    log.info("Starting Work server as guid {0}".format(guid))
    # Import all of the jobs we handle
    tasks = [
        Task('my.job1', job1),
        ]
    # Initialize the server
    server = GearmanTaskServer(
        host_list   = settings['gearman.servers'],
        tasks       = tasks,
        max_workers = settings['jobs.max_per_host'],
        id_prefix   = guid,
        GMWorker    = GearmanWorker,
        sighandler  = True,
        verbose     = True,
        )
    # Run the loop
    server.serve_forever()

