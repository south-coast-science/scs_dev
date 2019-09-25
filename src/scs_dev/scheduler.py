#!/usr/bin/env python3

"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The scheduler utility is used to provide timing and synchronisation to the sampling processes: climate_sampler,
gases_sampler, particulates_sampler, and status_sampler.

When started (typically as a background process) the scheduler utility launches one sub-process for each of the items
in the schedule configuration. On the given interval for each item, the sub-process releases a Posix semaphore to
the sampler, then regains it. The name of the semaphore is the name of the tag. By convention, the following
names are used:

* scs-climate
* scs-gases
* scs-particulates
* scs-status

The schedule configuration is specified using the scs_mfr/schedule utility.

SYNOPSIS
scheduler.py [-v]

EXAMPLES
scheduler.py

FILES
~/SCS/conf/schedule.json

DOCUMENT EXAMPLE
{"scs-climate": {"interval": 60.0, "tally": 1}, "scs-gases": {"interval": 5.0, "tally": 1},
"scs-particulates": {"interval": 10.0, "tally": 1}, "scs-status": {"interval": 60.0, "tally": 1}}

SEE ALSO
scs_dev/climate_sampler
scs_dev/gases_sampler
scs_dev/particulates_sampler
scs_dev/status_sampler
scs_mfr/schedule
"""

import sys
import time

from scs_core.sys.signalled_exit import SignalledExit

from scs_core.sync.schedule import Schedule

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_host.sys.host import Host
from scs_host.sync.scheduler import Scheduler


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    scheduler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdVerbose()

    if cmd.verbose:
        print("scheduler: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("scheduler", cmd.verbose)

        # Schedule...
        schedule = Schedule.load(Host)

        if schedule is None:
            print("scheduler: Schedule not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("scheduler: %s" % schedule, file=sys.stderr)
            sys.stderr.flush()

        # Scheduler...
        scheduler = Scheduler(schedule, True)          # cmd.verbose


        # ------------------------------------------------------------------------------------------------------------
        # run...

        scheduler.run()

        while True:
            time.sleep(1.0)

    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError, TypeError) as ex:
        print("scheduler: %s" % ex, file=sys.stderr)

    finally:
        if cmd and cmd.verbose:
            print("scheduler: finishing", file=sys.stderr)

        if scheduler:
            scheduler.stop()
