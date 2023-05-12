#!/usr/bin/env python3

"""
Created on 5 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The psu_monitor utility is used to report on the PSU status, and to manage shutdown events initiated by the user
(operations pin / switch / shutdown button) or by the PSU itself (loss of power).

If the --config-interval flag is used, frequency of reporting is specified by the PSU configuration. Alternatively,
the reporting interval can be set explicitly with the --interval flag. Note that the frequency of polling for user
and PSU events is hard-coded, and is typically every second.

If no interval is specified, then the psu_monitor utility delivers one report and stops.

Unless inhibited by the --no-output flag, the report is writen to stdout. If the PSU configuration specifies a report
file path, then the PSU status report is (also) written to this file. When the utility terminates, the file is deleted.

The status_sampler utility reads the PSU report file, if available. The psu_monitor reporting frequency should
therefore be set to match the status_sampler reporting frequency.

SYNOPSIS
psu_monitor.py [{ -c | -i INTERVAL } [-x] [-o]] [-v]

EXAMPLES
./psu_monitor.py -i 60 -x

DOCUMENT EXAMPLE - OUTPUT
{"src": "Cv1", "standby": false, "in": true, "pwr-in": 11.5, "chgr": "TFTF",
"batt": {"chg": 99, "tte": null, "ttf": null}, "prot-batt": 4.1}

SEE ALSO
scs_dev/status_sampler
scs_mfr/conf
"""

import sys

from scs_core.data.json import JSONify

from scs_core.sync.interval_timer import IntervalTimer

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_psu_monitor import CmdPSUMonitor

from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_psu.psu.psu_conf import PSUConf


# TODO: add mode where shutdown happens N minutes since DC in?
# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    psu_conf = None
    psu_monitor = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPSUMonitor()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    # logging...
    Logging.config('psu_monitor', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Utilities.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)
        interface = None if interface_conf is None else interface_conf.interface()
        interface_model = None if interface_conf is None else interface_conf.model

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)

        if psu_conf is None:
            logger.error("PSUConf not available.")
            exit(1)

        logger.info(psu_conf)

        psu_monitor = psu_conf.psu_monitor(Host, interface_model, cmd.ignore_standby)

        if psu_monitor is None:
            logger.error("PSUMonitor not available.")
            exit(1)

        logger.info(psu_monitor)

        # IntervalTimer...
        if cmd.config_interval and psu_conf.reporting_interval is None:
            logger.error("PSUConf reporting interval is None.")
            exit(1)

        interval = psu_conf.reporting_interval if cmd.config_interval else cmd.interval
        timer = IntervalTimer(interval)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("psu_monitor", cmd.verbose)

        psu_monitor.start()

        while timer.true():
            status = psu_monitor.sample()

            if status is None:
                continue

            status.save(psu_conf.report_file)

            if cmd.output:
                print(JSONify.dumps(status.as_json()))
                sys.stdout.flush()

            if cmd.single_shot_mode():
                break


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        logger.info("finishing")

        if psu_monitor:
            psu_monitor.stop()

        if psu_conf:
            Filesystem.rm(psu_conf.report_file)

        I2C.Utilities.close()
