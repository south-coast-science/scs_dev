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
* sht.hmd, sht.tmp - humidity and temperature at point of sampling (OPC-N3 only)

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
* a source identifier ("N2" or "N3")
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
particulates_sampler.py [-f FILE] [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./particulates_sampler.py -v -f /home/pi/SCS/conf/opc_conf_cs1.json

FILES
~/SCS/conf/opc_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLES
OPC-N2:
{"tag": "scs-be2-2", "src": "N2", "rec": "2018-11-11T09:05:10.424+00:00",
"val": {"per": 10.0, "pm1": 8.1, "pm2p5": 12.1, "pm10": 12.9,
"bins": [142, 63, 48, 28, 10, 13, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
"mtf1": 42, "mtf3": 44, "mtf5": 46, "mtf7": 59}}

OPC-N3:
{"tag": "scs-be2-3", "src": "N3", "rec": "2018-11-17T12:06:45.605+00:00",
"val": {"per": 4.5, "pm1": 12.0, "pm2p5": 19.6, "pm10": 79.0,
"bins": [708, 27, 8, 3, 3, 3, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
"mtf1": 81, "mtf3": 98, "mtf5": 97, "mtf7": 118,
"sht": {"hmd": 37.3, "tmp": 24.7}}}

SEE ALSO
scs_dev/opc_cleaner
scs_dev/opc_power
scs_dev/opc_version
scs_dev/scheduler
scs_mfr/opc_cleaning_interval
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



# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("particulates_sampler: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
            print("particulates_sampler: %s" % system_id, file=sys.stderr)

        # OPCConf...
        opc_conf = OPCConf.load_from_file(cmd.file) if cmd.file else OPCConf.load(Host)

        if opc_conf is None:
            print("particulates_sampler: OPCConf not available.", file=sys.stderr)
            exit(1)

        if cmd.samples > 1 and cmd.interval < opc_conf.sample_period:
            print("particulates_sampler: interval (%d) must not be less than opc_conf sample period (%d)." %
                  (cmd.interval, opc_conf.sample_period), file=sys.stderr)
            exit(1)

        # OPCMonitor...
        opc_monitor = opc_conf.opc_monitor(Host)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        # sampler...
        sampler = ParticulatesSampler(runner, tag, opc_monitor)

        if cmd.verbose:
            print("particulates_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()

        # I2C...
        opc = opc_conf.opc(Host)
        i2c_bus = Host.I2C_SENSORS if opc.uses_spi() else opc.bus

        I2C.open(i2c_bus)


        # ------------------------------------------------------------------------------------------------------------
        # wait until needed...

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

        for sample in sampler.samples():
            if sample is None:
                continue

            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s: particulates: %s" % (now.as_time(), sample.rec.as_time()), file=sys.stderr)
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
