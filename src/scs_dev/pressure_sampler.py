#!/usr/bin/env python3

"""
Created on 21 Jun 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The pressure_sampler utility reads an ICP-10101 or MPL115A2 digital barometer. It reports pressure in kilopascals and
temperature in Centigrade. The utility always reports the actual atmospheric pressure (pA). It additionally reports
temperature and equivalent pressure at sea level (p0) depending on whether the host device's  altitude has been
configured and the MPL115A2's temperature sensor has been calibrated.

The pressure_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document
with fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
pressure_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [{ -v | -d }]

EXAMPLES
./pressure_sampler.py -i10

FILES
~/SCS/conf/mpl115a2_calib.json
~/SCS/conf/pressure_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - v0
{"rec": "2021-10-06T11:34:18Z", "tag": "scs-be2-3",
"val": {"bar": {"pA": 102.3, "p0": 103.5, "tmp": 24.0}}}

DOCUMENT EXAMPLE - v1
{"rec": "2021-10-11T11:08:24Z", "tag": "scs-be2-3", "ver": 1.0,
"val": {"bar": {"pA": 103.5, "p0": 104.7, "tmp": 22.6}}}


SEE ALSO
scs_dev/scheduler
scs_mfr/mpl115a2_calib
scs_mfr/pressure_conf
scs_mfr/schedule
scs_mfr/system_id

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.climate.mpl115a2_calib import MPL115A2Calib

from scs_core.data.json import JSONify

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.pressure_sampler import PressureSampler

from scs_dfe.climate.pressure_conf import PressureConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    # logging...
    Logging.config('climate_sampler', level=cmd.log_level())
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Sensors.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id:
            logger.info(system_id)

        # PressureConf...
        conf = PressureConf.load(Host)

        if conf is None:
            logger.error("PressureConf not available.")
            exit(1)

        logger.info(conf)

        # MPL115A2Calib...
        mpl_calib = MPL115A2Calib.load(Host)

        if mpl_calib is not None:
            logger.info(mpl_calib)

        # barometer...
        barometer = conf.sensor(mpl_calib)

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        sampler = PressureSampler(runner, tag, barometer, conf.altitude)

        logger.info(sampler)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("pressure_sampler", cmd.verbose)

        sampler.init()

        for sample in sampler.samples():
            # report...
            logger.info("rec: %s" % sample.rec.as_time())

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(ex)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd:
            logger.info("finishing")

        I2C.Sensors.close()
