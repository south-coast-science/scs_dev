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

from scs_dfe.board.dfe_conf import DFEConf
from scs_dfe.gps.gps_conf import GPSConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# TODO: ! fix bug where status waits for GPS receiver
# TODO: ! fix bug where status waits for PSU

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

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
        dfe_conf = DFEConf.load(Host)
        board = None if dfe_conf is None else dfe_conf.board_temp_sensor()

        if cmd.verbose and dfe_conf:
            print(dfe_conf, file=sys.stderr)

        # GPS...
        gps_conf = GPSConf.load(Host)
        gps_monitor = None if gps_conf is None else gps_conf.gps_monitor(Host)

        if cmd.verbose and gps_monitor:
            print(gps_monitor, file=sys.stderr)

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)
        psu_monitor = None if psu_conf is None else psu_conf.psu_monitor(Host)

        if cmd.verbose and psu_monitor:
            print(psu_monitor, file=sys.stderr)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        # sampler...
        sampler = StatusSampler(runner, system_id, board, gps_monitor, psu_monitor)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        sampler.start()

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
        if sampler:
            sampler.stop()

        I2C.close()
