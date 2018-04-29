#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The particulates_sampler utility reads a set of values from the Alphasense optical particle counter (OPC). The reported
values are:

* per - the period of time between the previous reading and this reading
* pm1, pm2p5, pm10 - particulate densities of PM1, PM2.5 and PM10 in ug/m3
* bins - the particle count, for particles of increasing size
* mtf1, mtf3, mtf5, mtf7 - time taken for particle movement between system points

The particulates_sampler utility operates by launching a background process. This OPCMonitor process reads the OPC
values at specified intervals (which may be different from the intervals used by the parent process). In addition,
the process power cycles the OPC if its laser safety control has tripped.

The scs_mfr/opc_conf utility is used to specify the OPC model, background process sampling time, and OPC control
power saving mode.

When the particulates_sampler utility starts, it power cycles the OPC. When the utility stops, it stops operations
on the OPC, and stops the OPC fan.

The particulates_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON
document with fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
particulates_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./particulates_sampler.py -v -s scs-particulates

FILES
~/SCS/conf/opc_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE
{"tag": "scs-bgx-122", "rec": "2018-04-05T10:57:49.178+00:00",
"val": {"per": 10.0, "pm1": 4.4, "pm2p5": 6.6, "pm10": 11.1,
"bins": {"0": 265, "1": 38, "2": 45, "3": 18, "4": 7, "5": 9, "6": 11, "7": 3, "8": 3, "9": 1,
"10": 0, "11": 0, "12": 0, "13": 0, "14": 0, "15": 0},
"mtf1": 19, "mtf3": 27, "mtf5": 29, "mtf7": 29}}

SEE ALSO
scs_dev/scheduler
scs_mfr/opc_conf
scs_mfr/schedule
scs_mfr/system_id

BUGS
Because readings are time-sensitive, the particulates_sampler utility is not process-safe - it should therefore be run
by only one process at a time.

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys
import time

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# TODO: see Experiments/System Technical Issues/Weird particulates startup/syslog Apr 13 14:33:51

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

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
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
        sampler = ParticulatesSampler(runner, tag, opc_monitor)

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

    finally:
        if sampler:
            sampler.stop()

        I2C.close()
