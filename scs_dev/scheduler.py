#!/usr/bin/env python3

"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires Schedule document.

command line example:
./scheduler.py -v
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sync.schedule import Schedule
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_verbose import CmdVerbose

from scs_host.sys.host import Host
from scs_host.sync.scheduler import Scheduler


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    cmd = None
    scheduler = None

    try:
        # ------------------------------------------------------------------------------------------------------------
        # cmd...

        cmd = CmdVerbose()

        if cmd.verbose:
            print(cmd, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Schedule...
        schedule = Schedule.load(Host)

        if schedule is None:
            print("Schedule not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(schedule, file=sys.stderr)
            sys.stderr.flush()

        # Scheduler...
        scheduler = Scheduler(schedule, cmd.verbose)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        scheduler.run()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("scheduler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if scheduler:
            scheduler.terminate()
