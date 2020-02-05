#!/usr/bin/env python3

"""
Created on 5 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The psu_monitor utility is used to

SYNOPSIS
psu_monitor.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [{ -x | -o }] [-v]

EXAMPLES
./psu_monitor.py -i 60

FILES
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2019-03-09T12:05:10Z", "val":
{"airnow": {"site": "850MM123456789", "pocs": {"88102": 2, "88103": 3}},
"tz": {"name": "Europe/London", "utc-offset": "+00:00"},
"sch": {"scs-climate": {"interval": 60.0, "tally": 1}, "scs-gases": {"interval": 10.0, "tally": 1},
"scs-particulates": {"interval": 10.0, "tally": 1}, "scs-status": {"interval": 60.0, "tally": 1}},
"tmp": {"brd": 30.2, "hst": 47.8},
"up": {"period": "00-18:30:00", "users": 2, "load": {"av1": 0.0, "av5": 0.0, "av15": 0.0}}}}

SEE ALSO
scs_dev/scheduler
"""

import sys
import time

from scs_core.aqcsv.conf.airnow_site_conf import AirNowSiteConf

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_psu_monitor import CmdStatusSampler
from scs_dev.sampler.psu_monitor import StatusSampler

from scs_dfe.gps.gps_conf import GPSConf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# TODO: move PSUMonitor into separate command line utility

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdStatusSampler()

    if cmd.verbose:
        print("psu_monitor: %s" % cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)
        interface = None if interface_conf is None else interface_conf.interface()
        interface_model = None if interface_conf is None else interface_conf.model

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)

        if psu_conf is None:
            print("psu_monitor: PSUConf not available.", file=sys.stderr)
            exit(1)

        psu_monitor = psu_conf.psu_monitor(Host, interface_model, not cmd.no_shutdown)

        if psu_monitor is None:
            print("psu_monitor: PSUMonitor not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("psu_monitor: %s" % psu_monitor, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("psu_monitor", cmd.verbose)

        psu_monitor.start()
        psu_monitor.join()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("psu_monitor: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("psu_monitor: finishing", file=sys.stderr)

        if sampler:
            sampler.stop()

        I2C.close()
