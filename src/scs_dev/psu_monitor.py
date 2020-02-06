#!/usr/bin/env python3

"""
Created on 5 Feb 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The psu_monitor utility is used to report on the PSU status, and to manage shutdown events initiated by the user
(operations pin / switch / shutdown button) or by the PSU itself (loss of power).

Frequency of reporting is specified by the --interval flag. Note that the frequency of polling for user and PSU
events is hard-coded, and is typically every second.

Unless inhibited by the --no-output flag, the report is written to stdout. If the PSU configuration specifies a report
file path, then the PSU status report is (also) written to this file. When the utility terminates, the file is deleted.

The status_sampler utility reads the PSU report file, if available. The psu_monitor reporting frequency should
therefore be set to match the status_sampler reporting frequency.

SYNOPSIS
psu_monitor.py -i INTERVAL [-x] [-o] [-v]

EXAMPLES
./psu_monitor.py -i 60

DOCUMENT EXAMPLE - OUTPUT
{"rst": "00", "standby": false, "chg": "0000", "batt-flt": false, "host-3v3": 3.3, "pwr-in": 15.6, "prot-batt": 0.0}

SEE ALSO
scs_dev/status_sampler
scs_mfr/psu_conf
"""

import sys

from scs_core.data.json import JSONify

from scs_core.sync.interval_timer import IntervalTimer

from scs_core.sys.filesystem import Filesystem
from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_psu_monitor import CmdPSUMonitor

from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

from scs_psu.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    psu_conf = None
    psu_monitor = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPSUMonitor()

    if cmd.verbose:
        print("psu_monitor: %s" % cmd, file=sys.stderr)

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)
        interface = None if interface_conf is None else interface_conf.interface()
        interface_model = None if interface_conf is None else interface_conf.model

        # PSUMonitor...
        psu_conf = PSUConf.load(Host)

        if psu_conf is None:
            print("psu_monitor: PSUConf not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("psu_monitor: %s" % psu_conf, file=sys.stderr)

        psu_monitor = psu_conf.psu_monitor(Host, interface_model, cmd.shutdown)

        if psu_monitor is None:
            print("psu_monitor: PSUMonitor not available.", file=sys.stderr)
            exit(1)

        if cmd.verbose:
            print("psu_monitor: %s" % psu_monitor, file=sys.stderr)
            sys.stderr.flush()

        # IntervalTimer...
        timer = IntervalTimer(cmd.interval)

        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("psu_monitor", cmd.verbose)

        psu_monitor.start()

        while timer.true():
            status = psu_monitor.sample()
            status.save(psu_conf.report_file)

            if cmd.output:
                print(JSONify.dumps(status.as_json()))
                sys.stdout.flush()


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError) as ex:
        print("psu_monitor: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("psu_monitor: finishing", file=sys.stderr)

        if psu_monitor:
            psu_monitor.stop()

        if psu_conf:
            Filesystem.rm(psu_conf.report_file)

        I2C.close()
