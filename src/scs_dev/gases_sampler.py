#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The gases_sampler utility reads a set of values from a South Coast Science digital front-end (DFE) board hosting an
Alphasense analogue front-end (AFE) board. The also utility reads an NDIR CO2 sensor, if the appropriate configuration
document is present.

The gases_sampler utility reports raw electrode voltages, temperature-compensated voltages, and gas concentrations
(in parts per billion) derived according to the relevant Alphasense application notes. If the AFE board includes a
Pt1000 temperature sensor, then the gases_sampler utility may also report the Pt1000 voltage and temperature.

The DFE board supports AFEs with up to four electrochemical sensors, or three electrochemical sensors plus one
photo-ionisation detector (PID). Before using the gases_sampler utility, the configuration of the AFE must be
specified using the scs_mfr/afe_calib utility.

Temperature must be known in order to perform a simple data interpretation. The gases_sampler utility applies an
order of precedence for temperature sources, depending on availability:

1. Sensirion SHT in A4 package
2. Free-to-air Sensirion SHT
3. AFE Pt1000 sensor

The presence of the DFE subsystem, and the availability of the Pt1000 sensor on the AFE is specified using the
scs_mfr/interface_conf utility. The configuration of Sensirion SHT sensor(s) is specified using the
scs_mfr/interface_conf utility.

Gas concentrations for each sensor are adjusted according to a baseline value, which is specified using the
scs_mfr/afe_baseline utility. This provides a simple way of managing zero-offset drift for each sensor
expressed in parts per billion.

The gases_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document with
fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

Support for the Alphasense NDIR was withdrawn on 9 Sep 2020.

SYNOPSIS
gases_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./gases_sampler.py -i10

FILES
~/SCS/conf/afe_baseline.json
~/SCS/conf/afe_calib.json
~/SCS/conf/interface_conf.json
~/SCS/conf/scd30_conf.json
~/SCS/conf/pt1000_calib.json
~/SCS/conf/scd30_conf.json
~/SCS/conf/sht_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2018-04-05T09:16:12.751+00:00",
"val": {"CO": {"weV": 0.34863, "aeV": 0.268817, "weC": 0.064464, "cnc": 237.0},
"SO2": {"weV": 0.277004, "aeV": 0.276129, "weC": -0.000801, "cnc": 2.2},
"H2S": {"weV": 0.258504, "aeV": 0.222316, "weC": -0.091086, "cnc": 7.2},
"VOC": {"weV": 0.102127, "weC": 0.101793, "cnc": 1294.8},
"sht": {"hmd": 54.4, "tmp": 21.6}}}

SEE ALSO
scs_dev/scheduler
scs_mfr/afe_baseline
scs_mfr/afe_calib
scs_mfr/gas_inference_conf
scs_mfr/interface_conf
scs_mfr/scd30_conf
scs_mfr/pt1000_calib
scs_mfr/schedule
scs_mfr/sht_conf
scs_mfr/system_id

RESOURCES
Alphasense Application Note AAN 803-02
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys
import time

from scs_core.climate.mpl115a2_calib import MPL115A2Calib

from scs_core.data.json import JSONify

from scs_core.gas.afe_calib import AFECalib

from scs_core.sample.gases_sample import GasesSample

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_core.model.gas.gas_model_conf import GasModelConf

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.mpl115a2_conf import MPL115A2Conf
from scs_dfe.climate.sht_conf import SHTConf

from scs_dfe.gas.scd30.scd30_conf import SCD30Conf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.comms.domain_socket import DomainSocket
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    interface = None
    client = None
    sampler = None
    scd30 = None

    afe_calib = None
    t_regression = None
    rh_regression = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    # logging...
    Logging.config('gases_sampler', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Sensors.open()
        I2C.Utilities.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Schedule...
        schedule = Schedule.load(Host)

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id:
            logger.info(system_id)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            logger.error("InterfaceConf not available.")
            exit(1)

        interface = interface_conf.interface()

        if interface is None:
            logger.error("Interface not available.")
            exit(1)

        if interface:
            logger.info(interface)

        # MPL115A2...
        mpl115a2_conf = MPL115A2Conf.load(Host)
        mpl115a2_calib = MPL115A2Calib.load(Host)

        mpl115a2 = None if mpl115a2_conf is None else mpl115a2_conf.mpl115a(mpl115a2_calib)

        if mpl115a2_conf:
            logger.info(mpl115a2_conf)

        # NDIR...
        scd30_conf = SCD30Conf.load(Host)
        scd30 = None if scd30_conf is None else scd30_conf.scd30()

        if scd30_conf and (0 < cmd.interval <= scd30_conf.sample_interval):
            logger.error("interval (%d) must be grater than SCD30Conf sample interval (%d)." %
                         (cmd.interval, scd30_conf.sample_interval))
            exit(2)

        if scd30_conf:
            logger.info(scd30_conf)

        # SHT...
        sht_conf = SHTConf.load(Host)
        sht = None if sht_conf is None else sht_conf.ext_sht()

        if sht_conf:
            logger.info(sht_conf)

        # gas_sensors...
        a4_sensors = interface.gas_sensors(Host)

        if a4_sensors:
            logger.info(a4_sensors)

        # GasModelConf...
        inference_conf = GasModelConf.load(Host)

        if inference_conf:
            logger.info(inference_conf)

            # AFECalib...                           # TODO: will need to support DSICalib
            afe_calib = AFECalib.load(Host)

            if afe_calib is None:
                logger.error("AFECalib not available.")
                exit(1)

            if afe_calib.calibrated_on is None:
                logger.error("AFECalib has no calibration date.")
                exit(1)

            # slope regression...
            if schedule is None or schedule.item('scs-gases') is None:
                logger.error("Schedule not available.")
                exit(1)

            # inference client...
            client = inference_conf.client(Host, DomainSocket, schedule.item('scs-gases'), afe_calib)
            client.wait_for_server()

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        sampler = GasesSampler(runner, tag, mpl115a2, scd30, sht, a4_sensors)

        logger.info(sampler)


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if cmd.semaphore and (schedule is None or not schedule.contains(cmd.semaphore)):
            logger.info("no schedule - halted.")

            while True:
                time.sleep(60.0)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        interface.power_gases(True)
        sampler.init(scd30_conf)

        # signal handler...
        SignalledExit.construct("gases_sampler", cmd.verbose)

        for sample in sampler.samples():
            logger.info("       rec: %s" % sample.rec.as_time())

            # inference...
            if inference_conf:
                inference = client.infer(sample, interface.status().temp)

                if inference is None:
                    logger.error("inference rejected: %s" % JSONify.dumps(sample))
                    continue

                sample = GasesSample.construct_from_jdict(inference)

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

        if client:
            client.close()

        if scd30:
            scd30.stop_periodic_measurement()

        if interface:
            interface.power_gases(False)

        I2C.Sensors.close()
        I2C.Utilities.close()
