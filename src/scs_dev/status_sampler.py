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

* Timezone
* GPS location
* Power supply condition
* Temperature of the host processor

The status_sampler writes its output to stdout. As for all sensing utilities, the output format is a JSON document with
fields for:

* the unique tag of the device
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
{"tag": "scs-ap1-6", "rec": "2018-04-05T14:17:01.943+00:00",
"val": {"tz": {"name": "Europe/London", "utc-offset": "+01:00"},
"sch": {"scs-climate": {"interval": 60.0, "tally": 1}, "scs-gases": {"interval": 5.0, "tally": 1},
"scs-particulates": {"interval": 10.0, "tally": 1}, "scs-status": {"interval": 60.0, "tally": 1}},
"tmp": {"brd": 27.6, "hst": 42.9}, "up": {"period": "00-00:08:00.000",
"users": 3, "load": {"av1": 0.0, "av5": 0.09, "av15": 0.08}}}}

SEE ALSO
scs_dev/scheduler
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

from scs_core.data.json import JSONify
from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sync.timed_runner import TimedRunner

from scs_core.sys.system_id import SystemID

from scs_dev.cmd.cmd_sampler import CmdSampler
from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.board.dfe_conf import DFEConf
from scs_dfe.gps.gps_conf import GPSConf

from scs_host.bus.i2c import I2C
from scs_host.sync.schedule_runner import ScheduleRunner
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# TODO: an absent system ID should result in an absent tag field.

# TODO: deal with the case of slow-to-start subsystem monitors

# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    sampler = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdSampler()

    if cmd.verbose:
        print(cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # SystemID...
        system_id = SystemID.load(Host)

        if system_id is None:
            print("status_sampler: SystemID not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print(system_id, file=sys.stderr)

        # board...
        dfe_conf = DFEConf.load(Host)
        board = None if dfe_conf is None else dfe_conf.board_temp_sensor()

        if cmd.verbose and dfe_conf:
            print(dfe_conf, file=sys.stderr)

        # GPS...
        gps_conf = GPSConf.load(Host)
        gps_monitor = None if gps_conf is None else gps_conf.gps_monitor(Host)

        if cmd.verbose and gps_monitor:
            print(gps_monitor, file=sys.stderr)

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)
        psu_monitor = None if psu_conf is None else psu_conf.psu_monitor(Host)

        if cmd.verbose and psu_monitor:
            print(psu_monitor, file=sys.stderr)

        # runner...
        runner = TimedRunner(cmd.interval, cmd.samples) if cmd.semaphore is None \
            else ScheduleRunner(cmd.semaphore, False)

        # sampler...
        sampler = StatusSampler(runner, system_id.message_tag(), board, gps_monitor, psu_monitor)

        if cmd.verbose:
            print(sampler, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        sampler.start()

        for sample in sampler.samples():
            if cmd.verbose:
                now = LocalizedDatetime.now()
                print("%s:       status: %s" % (now.as_iso8601(), sample.rec.as_iso8601()), file=sys.stderr)
                sys.stderr.flush()

            print(JSONify.dumps(sample))
            sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except KeyboardInterrupt:
        if cmd.verbose:
            print("status_sampler: KeyboardInterrupt", file=sys.stderr)

    finally:
        if sampler:
            sampler.stop()

        I2C.close()
