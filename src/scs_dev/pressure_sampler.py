#!/usr/bin/env python3

"""
Created on 21 Jun 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The pressure_sampler utility reads a MPL115A2 digital barometer. It reports pressure in kilopascals and temperature
in Centigrade. The utility always reports the actual atmospheric pressure (pA). It additionally reports temperature
and equivalent pressure at sea level (p0) depending on whether the host device's  altitude has been configured and the
MPL115A2's temperature sensor has been calibrated.

The pressure_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document
with fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
pressure_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./pressure_sampler.py -i10

FILES
~/SCS/conf/mpl115a2_calib.json
~/SCS/conf/mpl115a2_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-be2-3", "rec": "2018-06-21T16:13:52.675+00:00", "val": {"pA": 102.2, "p0": 113.8, "tmp": 25.6}}

SEE ALSO
scs_dev/scheduler
scs_mfr/mpl115a2_calib
scs_mfr/mpl115a2_conf
scs_mfr/schedule
scs_mfr/system_id

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.climate.mpl115a2_calib import MPL115A2Calib

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.pressure_sampler import PressureSampler

from scs_dfe.climate.mpl115a2_conf import MPL115A2Conf
from scs_dfe.climate.mpl115a2 import MPL115A2

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("pressure_sampler: %s" % cmd, file=sys.stderr)

    try:
        I2C.Sensors.open()


        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
            print("pressure_sampler: %s" % system_id, file=sys.stderr)

        # MPL115A2Conf...
        conf = MPL115A2Conf.load(Host)

        if conf is None:
            print("pressure_sampler: MPL115A2Conf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("pressure_sampler: %s" % conf, file=sys.stderr)

        # MPL115A2Calib...
        calib = MPL115A2Calib.load(Host)

        if cmd.verbose and calib is not None:
            print("pressure_sampler: %s" % calib, file=sys.stderr)

        # MPL115A2...
        barometer = MPL115A2.construct(calib)

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        sampler = PressureSampler(runner, tag, barometer, conf.altitude)

        if cmd.verbose:
            print("pressure_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("pressure_sampler", cmd.verbose)

        sampler.init()

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now().utc()
                print("%s:     pressure: %s" % (now.as_time(), sample.rec.as_time()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("pressure_sampler: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("pressure_sampler: finishing", file=sys.stderr)

        I2C.Sensors.close()
