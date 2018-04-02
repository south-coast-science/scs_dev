#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The XX utility is used to .

EXAMPLES
xx

FILES
~/SCS/aws/

DOCUMENT EXAMPLE
xx

SEE ALSO
scs_dev/



Requires SystemID document.

command line example:
./particulates_sampler.py -i 10 | \
./osio_topic_publisher.py -e /users/southcoastscience-dev/test/particulates
"""

import sys
import time

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID
from scs_core.sys.exception_report import ExceptionReport

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)


    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        I2C.open(Host.I2C_SENSORS)

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("particulates_sampler: SystemID not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # OPCConf...
        opc_conf = OPCConf.load(Host)

        if opc_conf is None:
            print("particulates_sampler: OPCConf not available.", file=sys.stderr)
            exit(1)

        # OPCMonitor...
        opc_monitor = opc_conf.opc_monitor(Host)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        # sampler...
        sampler = ParticulatesSampler(runner, system_id.message_tag(), opc_monitor)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # wait until needed...

        # TODO: why wait for a schedule item?

        if cmd.semaphore:
            while True:
                schedule = Schedule.load(Host)
                item = None if schedule is None else schedule.item(ParticulatesSampler.SCHEDULE_SEMAPHORE)

                if item:
                    break

                time.sleep(1.0)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        sampler.start()

        if cmd.verbose:
            print(opc_monitor.firmware(), file=sys.stderr)
            sys.stderr.flush()

        for sample in sampler.samples():
            if sample is None:
                continue

            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s: particulates: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("particulates_sampler: KeyboardInterrupt", file=sys.stderr)

    except Exception as ex:
        print(JSONify.dumps(ExceptionReport.construct(ex)), file=sys.stderr)

    finally:
        if sampler:
            sampler.stop()

        I2C.close()
