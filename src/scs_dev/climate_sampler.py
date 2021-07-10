#!/usr/bin/env python3

"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The climate_sampler utility reads a Sensirion SHT 31 (or equivalent) sensor - it therefore provides a measurement of
temperature and relative humidity. Output values are in degrees centigrade and percentage, respectively.

The climate_sampler utility may also read an ICP-10101 or MPL115A2 digital barometer. Depending on configuration, the
report from this sensor includes absolute pressure (pA), and optionally equivalent sea-level pressure (p0) and the
MPL115A2 temperature. Pressure is reported in kilo pascals.

The climate_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document
with fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

South Coast Science equipment may carry one or two SHT sensors. The configuration is specified by the
scs_mfr/sht_conf utility.

SYNOPSIS
climate_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./climate_sampler.py -i10

FILES
~/SCS/conf/mpl115a2_calib.json
~/SCS/conf/mpl115a2_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/sht_conf.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2019-01-22T14:12:04Z", "val": {"hmd": 50.5, "tmp": 21.1, "bar": {"pA": 99.7}}}

SEE ALSO
scs_dev/scheduler
scs_mfr/mpl115a2_calib
scs_mfr/pressure_conf
scs_mfr/schedule
scs_mfr/sht_conf
scs_mfr/system_id

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys
import time

from scs_core.climate.mpl115a2_calib import MPL115A2Calib

from scs_core.data.json import JSONify

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.climate_sampler import ClimateSampler

from scs_dfe.climate.pressure_conf import PressureConf
from scs_dfe.climate.sht_conf import SHTConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    barometer = None
    altitude = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    # logging...
    Logging.config('climate_sampler', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Sensors.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Schedule...
        schedule = Schedule.load(Host)

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id:
            logger.info(system_id)

        # SHTConf...
        sht_conf = SHTConf.load(Host)

        if sht_conf is None:
            logger.error("SHTConf not available.")
            exit(1)

        logger.info(sht_conf)

        # SHT...
        sht = sht_conf.ext_sht()

        # PressureConf...
        pressure_conf = PressureConf.load(Host, default=None)

        if pressure_conf is not None:
            logger.info(pressure_conf)

            altitude = pressure_conf.altitude

            # MPL115A2Calib...
            mpl_calib = MPL115A2Calib.load(Host)

            if mpl_calib is not None:
                logger.info(mpl_calib)

            # MPL115A2...
            barometer = pressure_conf.sensor(mpl_calib)

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        sampler = ClimateSampler(runner, tag, sht, barometer, altitude)
        logger.info(sampler)


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if cmd.semaphore and (schedule is None or not schedule.contains(cmd.semaphore)):
            logger.info("no schedule - halted.")

            while True:
                time.sleep(60.0)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("climate_sampler", cmd.verbose)

        if barometer is not None:
            barometer.init()

        for sample in sampler.samples():
            logger.info("     rec: %s" % sample.rec.as_time())

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
