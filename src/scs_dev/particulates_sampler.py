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

When the particulates_sampler utility starts, it power-cycles the OPC. When the utility stops, it stops operations
on the OPC, and stops the OPC fan.

The particulates_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON
document with fields for:

* tag - the unique tag of the device (if the system ID is set)
* src - a source identifier ("N2" or "N3")
* rec - the recording date / time in ISO 8601 format
* val - a value field containing the sensed values
* exg - data interpretations, as specified by opc_conf.py

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

If any errors are detected while the OPC is running, these are logged. the log can be interrogated using the
mfr/opc_error_log utility.

SYNOPSIS
particulates_sampler.py [-n NAME] [{ -s SEMAPHORE | -i INTERVAL [-c SAMPLES] }] [{ -v | -d }]

EXAMPLES
./particulates_sampler.py -v -f /home/pi/SCS/conf/opc_conf_cs1.json

FILES
~/SCS/conf/opc_conf.json
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json
~/SCS/log/opc_error_log.csv

DOCUMENT EXAMPLE - v0:
{"rec": "2021-10-11T11:06:57Z", "tag": "scs-bgx-431", "src": "N3",
"val": {"per": 4.1, "pm1": 1.7, "pm2p5": 6.3, "pm10": 24.1,
"bin": [106, 31, 25, 5, 9, 5, 2, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
"mtf1": 34, "mtf3": 34, "mtf5": 43, "mtf7": 48, "sfr": 3.66,
"sht": {"hmd": 37.3, "tmp": 23.8}},
"exg": {"rn20": {"pm1": 3.6, "pm2p5": 5.5, "pm10": 27.1}}}

DOCUMENT EXAMPLE - v2:
{"rec": "2021-10-11T11:11:14Z", "tag": "scs-be2-3", "ver": 2.0, "src": "N3",
"val": {"per": 4.1, "pm1": 0.7, "pm2p5": 3.2, "pm10": 33.3,
"bin": [50, 24, 6, 2, 4, 2, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
"mtf1": 29, "mtf3": 32, "mtf5": 19, "mtf7": 54, "sfr": 3.73,
"sht": {"hmd": 43.6, "tmp": 25.6}},
"exg": {"src": "rn20", "val": {"pm1": 1.5, "pm2p5": 6.4, "pm10": 58.7}}}

SEE ALSO
scs_dev/interface_power
scs_dev/opc_cleaner
scs_dev/scheduler

scs_mfr/opc_cleaning_interval
scs_mfr/opc_conf
scs_mfr/opc_error_log
scs_mfr/opc_firmware_conf
scs_mfr/opc_version
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

from scs_core.model.pmx.pmx_model_conf import PMxModelConf

from scs_core.particulate.opc_version import OPCVersion

from scs_core.sample.particulates_sample import ParticulatesSample

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.comms.domain_socket import DomainSocket
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# TODO: support "empty" OPCConf when no OPC is present?
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    opc_conf = None

    opc = None
    sht = None
    client = None
    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    # logging...
    Logging.config('particulates_sampler', level=cmd.log_level())
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Schedule...
        schedule = Schedule.load(Host, skeleton=True)

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id:
            logger.info(system_id)

        # OPCConf...
        opc_conf = OPCConf.load(Host, name=cmd.name)

        if opc_conf is None:
            if cmd.name:
                logger.error("OPCConf '%s' not available." % cmd.name)
            else:
                logger.error("OPCConf not available.")
            exit(1)

        if 0 < cmd.interval < opc_conf.sample_period:
            logger.error("interval (%d) must not be less than opc_conf sample period (%d)." %
                         (cmd.interval, opc_conf.sample_period))
            exit(2)

        # I2C...
        I2C.Utilities.open()

        if opc_conf.uses_spi():
            I2C.Sensors.open()
        else:
            I2C.Sensors.open_for_bus(opc_conf.bus)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            logger.error("InterfaceConf not available.")
            exit(1)

        interface = interface_conf.interface()

        # PMxModelConf...
        inference_conf = PMxModelConf.load(Host)

        if inference_conf:
            logger.info(inference_conf)

            # inference client...
            client = inference_conf.client(Host, DomainSocket)
            client.wait_for_server()

            # SHT...
            sht_conf = SHTConf.load(Host)

            if sht_conf is None:
                logger.error("SHTConf not available.")
                exit(1)

            sht = sht_conf.ext_sht()
            logger.info(sht)

        # OPCMonitor...
        opc_monitor = opc_conf.opc_monitor(Host, interface)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        # sampler...
        sampler = ParticulatesSampler(runner, tag, opc_conf.restart_on_zeroes, opc_monitor)
        logger.info(sampler)


        # ------------------------------------------------------------------------------------------------------------
        # check...

        if cmd.semaphore and cmd.semaphore not in schedule:
            interface.power_opc(True)
            opc_monitor.operations_off()            # display may need the SPI power to remain on

            logger.info("no schedule - halted.")

            while True:
                time.sleep(60.0)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct()

        sampler.start()

        # update OPCVersion...
        version = OPCVersion(opc_monitor.opc.serial_no(), opc_monitor.opc.firmware(), name=cmd.name)
        version.save(Host)

        for opc_sample in sampler.samples():
            if opc_sample is None:
                continue

            if inference_conf:
                # climate...
                int_sht_sample = opc_sample.values.get('sht')

                try:
                    ext_sht_sample = None if sht is None else sht.sample()

                except OSError as ex:
                    ext_sht_sample = None
                    logger.error("SHT: %s" % ex)
                    exit(1)

                # inference...
                inference = client.infer(opc_sample, ext_sht_sample)

                if inference is None:
                    logger.error("inference rejected: %s" % JSONify.dumps(opc_sample))
                    continue

                opc_sample = ParticulatesSample.construct_from_jdict(inference)

            # report...
            logger.info("rec: %s" % opc_sample.rec.as_time())

            print(JSONify.dumps(opc_sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd:
            logger.info("finishing")

        if sampler:
            sampler.stop()

        if client:
            client.close()

        I2C.Utilities.close()
        I2C.Sensors.close()
