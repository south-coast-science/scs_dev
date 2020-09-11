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

* tag - the unique tag of the device (if the system ID is set)
* src - a source identifier ("N2" or "N3")
* rec - the recording date / time in ISO 8601 format
* val - a value field containing the sensed values
* exg - data interpretations, as specified by opc_conf.py

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

DOCUMENT EXAMPLE (OPC-N3):
{"tag": "scs-be2-3", "src": "N3", "rec": "2019-12-10T15:24:04Z",
"val": {"per": 4.9, "pm1": 5.6, "pm2p5": 6.7, "pm10": 6.8,
"bin": [338, 42, 4, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
"mtf1": 83, "mtf3": 101, "mtf5": 0, "mtf7": 0, "sfr": 0.61,
"sht": {"hmd": 32.1, "tmp": 30.7}},
"exg": {"iseceen2v1": {"pm1": 3.9, "pm2p5": 4.2, "pm10": 4.8},
"isecsen2v2": {"pm1": 4.7, "pm2p5": 5.1, "pm10": 6.1}}}

SEE ALSO
scs_dev/interface_power
scs_dev/opc_cleaner
scs_dev/scheduler

scs_mfr/opc_cleaning_interval
scs_mfr/opc_conf
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

import json
import logging
import sys
import time

from collections import OrderedDict

from scs_core.comms.uds_client import UDSClient

from scs_core.data.datetime import LocalizedDatetime
from scs_core.data.json import JSONify

try:
    from scs_exegesis.particulate.exegete_collection import ExegeteCollection
except ImportError:
    from scs_core.exegesis.particulate.exegete_collection import ExegeteCollection

from scs_core.exegesis.particulate.text import Text

from scs_core.sample.sample import Sample

from scs_core.sync.schedule import Schedule
from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    opc = None
    sht = None
    client = None
    sampler = None

    internal_sht_sample = None
    external_sht_sample = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("particulates_sampler: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # logger...
        logger = logging.getLogger(__name__)
        logging.basicConfig(stream=sys.stderr, level=logging.INFO)

        # Schedule...
        schedule = Schedule.load(Host)

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

        if 0 < cmd.interval < opc_conf.sample_period:
            print("particulates_sampler: interval (%d) must not be less than opc_conf sample period (%d)." %
                  (cmd.interval, opc_conf.sample_period), file=sys.stderr)
            exit(1)

        # I2C...
        i2c_bus = Host.I2C_SENSORS if opc_conf.uses_spi() else opc_conf.bus
        I2C.open(i2c_bus)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("particulates_sampler: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        # inference client...
        if opc_conf.inference:
            client = UDSClient(opc_conf.inference, logger)

            if cmd.verbose:
                print("particulates_sampler: %s" % client, file=sys.stderr)

        # exegetes...
        exegete_collection = ExegeteCollection.construct(opc_conf.exegete_names)

        for name in opc_conf.exegete_names:
            if not exegete_collection.has_member(name):
                print("particulates_sampler: WARNING: exegete '%s' is not available - ignoring." % name,
                      file=sys.stderr)
                sys.stderr.flush()

        # SHTConf...
        if exegete_collection.uses_external_sht() or opc_conf.inference:
            sht_conf = SHTConf.load(Host)

            if sht_conf is None:
                print("particulates_sampler: SHTConf not available.", file=sys.stderr)
                exit(1)

            # SHT...
            sht = sht_conf.ext_sht()

            if cmd.verbose:
                print("particulates_sampler: %s" % sht, file=sys.stderr)

        # OPCMonitor...
        opc_monitor = opc_conf.opc_monitor(interface, Host)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore)

        # sampler...
        sampler = ParticulatesSampler(runner, tag, opc_conf.restart_on_zeroes, opc_monitor)

        if cmd.verbose:
            print("particulates_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()

        # ------------------------------------------------------------------------------------------------------------
        # check...

        if cmd.semaphore and (schedule is None or not schedule.contains(cmd.semaphore)):
            interface.power_opc(True)
            opc_monitor.operations_off()            # display may need the SPI power to remain on

            if cmd.verbose:
                print("particulates_sampler: no schedule - stalled", file=sys.stderr)
                sys.stderr.flush()

            while True:
                time.sleep(1.0)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("particulates_sampler", cmd.verbose)

        sampler.start()

        if client:
            client.connect()

        for opc_sample in sampler.samples():
            if opc_sample is None:
                continue

            # climate...
            if exegete_collection.has_members() or opc_conf.inference:
                internal_sht_sample = opc_sample.values.get('sht')

                try:
                    external_sht_sample = None if sht is None else sht.sample()

                except OSError as ex:
                    external_sht_sample = None
                    print("particulates_sampler: %s" % ex, file=sys.stderr)
                    sys.stderr.flush()
                    exit(1)

            # exegesis...
            if exegete_collection.has_members():
                text = Text.construct_from_jdict(opc_sample.values)
                opc_sample.exegeses = exegete_collection.interpretation(text, internal_sht_sample, external_sht_sample)

            # inference...
            if opc_conf.inference:
                combined = {"particulates": opc_sample.as_json(), "climate": external_sht_sample.as_json()}

                client.request(JSONify.dumps(combined))
                response = client.wait_for_response()

                if response is None:
                    print("particulates_sampler: inference rejected for: %s" % combined, file=sys.stderr)
                    sys.stdout.flush()
                    continue

                else:
                    jdict = json.loads(response, object_hook=OrderedDict)
                    opc_sample = Sample.construct_from_jdict(jdict)

            # report...
            if cmd.verbose:
                now = LocalizedDatetime.now().utc()
                print("%s: particulates: %s" % (now.as_time(), opc_sample.rec.as_time()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(opc_sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("particulates_sampler: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("particulates_sampler: finishing", file=sys.stderr)

        if sampler:
            sampler.stop()

        if client:
            client.disconnect()

        I2C.close()
