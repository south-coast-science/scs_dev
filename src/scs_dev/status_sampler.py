#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

Requires SystemID document.

command line example:
./status_sampler.py -i 10 | ./osio_topic_publisher.py -e /users/southcoastscience-dev/test/status
"""

import sys

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.exception_report import ExceptionReport
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.gps.gps_conf import GPSConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    gps = None
    psu = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("SystemID not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # board...
        board = MCP9808(True)

        # GPS...
        gps_conf = GPSConf.load(Host)
        gps = gps_conf.gps(Host)

        # PSU...
        psu_conf = PSUConf.load(Host)
        psu = psu_conf.psu(Host)

        if cmd.verbose and psu:
            print(psu, file=sys.stderr)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        # sampler...
        sampler = StatusSampler(runner, system_id, board, gps, psu)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if psu:
            psu.open()

        if gps:
            gps.power_on()
            gps.open()

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:       status: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("status_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if gps:
            gps.close()

        if psu:
            psu.close()

        I2C.close()
