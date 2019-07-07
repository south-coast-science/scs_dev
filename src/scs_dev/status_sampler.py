#!/usr/bin/env python3

"""
Created on 5 Dec 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The status_sampler utility is used to report on the configuration and condition of the host system and its
peripherals. Items included in the report vary depending on the hardware configuration of the equipment. Fields
which are always reported include:

* Sensing schedule
* Unix uptime report
* Temperature of the digital front-end board

Fields which may be reported include:

* AirNowSiteConf
* Timezone
* GPS location
* Power supply condition
* Temperature of the host processor

The status_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document with
fields for:

* the unique tag of the device (if the system ID is set)
* the recording date / time in ISO 8601 format
* a value field containing the sensed values

Command-line options allow for single-shot reading, multiple readings with specified time intervals, or readings
controlled by an independent scheduling process via a Unix semaphore.

SYNOPSIS
status_sampler.py [{ -s SEMAPHORE | -i INTERVAL [-n SAMPLES] }] [-v]

EXAMPLES
./status_sampler.py -i60

FILES
~/SCS/conf/schedule.json
~/SCS/conf/system_id.json

DOCUMENT EXAMPLE - OUTPUT
{"tag": "scs-ap1-6", "rec": "2019-03-09T12:05:10Z", "val":
{"airnow": {"site": "850MM123456789", "pocs": {"88102": 2, "88103": 3}},
"tz": {"name": "Europe/London", "utc-offset": "+00:00"},
"sch": {"scs-climate": {"interval": 60.0, "tally": 1}, "scs-gases": {"interval": 10.0, "tally": 1},
"scs-particulates": {"interval": 10.0, "tally": 1}, "scs-status": {"interval": 60.0, "tally": 1}},
"tmp": {"brd": 30.2, "hst": 47.8},
"up": {"period": "00-18:30:00", "users": 2, "load": {"av1": 0.0, "av5": 0.0, "av15": 0.0}}}}

SEE ALSO
scs_dev/scheduler
scs_mfr/airnow_conf
scs_mfr/gps_conf
scs_mfr/psu_conf
scs_mfr/schedule
scs_mfr/system_id
scs_mfr/timezone

BUGS
If status_sampler is run in single-shot mode, GPS and PSU monitors may time out before being able to supply data.

RESOURCES
https://en.wikipedia.org/wiki/ISO_8601
"""

import sys

from scs_core.aqcsv.conf.airnow_site_conf import AirNowSiteConf

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.signalled_exit import SignalledExit
from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.gps.gps_conf import GPSConf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# TODO: deal with the case of slow-to-start subsystem monitors

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print("status_sampler: %s" % cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # signal handler...
        SignalledExit.construct("status_sampler", cmd.verbose)

        # SystemID...
        system_id = SystemID.load(Host)

        tag = None if system_id is None else system_id.message_tag()

        if system_id and cmd.verbose:
            print("status_sampler: %s" % system_id, file=sys.stderr)

        # AirNow...
        airnow = AirNowSiteConf.load(Host)

        if airnow and cmd.verbose:
            print("status_sampler: %s" % airnow, file=sys.stderr)

        # Interface...
        interface_conf = InterfaceConf.load(Host)
        interface = None if interface_conf is None else interface_conf.interface()

        if cmd.verbose and interface:
            print("status_sampler: %s" % interface, file=sys.stderr)

        # GPS...
        gps_conf = GPSConf.load(Host)
        gps_monitor = None if gps_conf is None else gps_conf.gps_monitor(Host, interface.load_switch_active_high)

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)
        psu_monitor = None if psu_conf is None else psu_conf.psu_monitor(Host)

        # sampler...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        sampler = StatusSampler(runner, tag, airnow, interface, gps_monitor, psu_monitor)

        if cmd.verbose:
            print("status_sampler: %s" % sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        sampler.start()

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:       status: %s" % (now.as_time(), sample.rec.as_time()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        if sampler:
            sampler.stop()

        I2C.close()
