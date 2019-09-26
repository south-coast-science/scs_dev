#!/usr/bin/env python3

"""
Created on 23 Jun 2019

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The display utility is used to set the content for a visual display, such as the Pimoroni Inky pHAT eInk module.
Content is gained from several sources:

* The display_conf settings
* System status
* Input from stdin or a Unix domain socket
* MQTT client and GPS receiver report files (if available)

SYNOPSIS
display.py [-v]

EXAMPLES
( cat < /home/pi/SCS/pipes/display_pipe & ) | /home/pi/SCS/scs_dev/src/scs_dev/display.py -v

SEE ALSO
scs_mfr/display_conf
scs_mfr/gps_conf
scs_mfr/mqtt_conf

RESOURCES
sudo apt install libatlas3-base
sudo apt-get install libopenjp2-7
"""

import sys

from scs_core.comms.mqtt_conf import MQTTConf

from scs_core.display.display_conf import DisplayConf

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_display import CmdDisplay
from scs_dev.handler.uds_reader import UDSReader

from scs_dfe.gps.gps_conf import GPSConf

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    monitor = None

    # ------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdDisplay()

    if cmd.verbose:
        print("display: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # MQTTConf...
        mqtt_conf = MQTTConf.load(Host)
        queue_report_filename = None if mqtt_conf is None else mqtt_conf.report_file

        # GPSConf...
        gps_conf = GPSConf.load(Host)
        gps_report_filename = None if gps_conf is None else gps_conf.report_file

        # UDSReader...
        reader = UDSReader(cmd.uds)

        if cmd.verbose and cmd.uds:
            print("display: %s" % reader, file=sys.stderr)

        # DisplayConf...
        conf = DisplayConf.load(Host)

        if conf is None:
            print("display: DisplayConf not available.", file=sys.stderr)
            exit(1)

        monitor = conf.monitor(queue_report_filename, gps_report_filename)

        if cmd.verbose and monitor:
            print("display: %s" % monitor, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        monitor.start()

        # signal handler...
        SignalledExit.construct("display", cmd.verbose)

        reader.connect()

        for message in reader.messages():
            if cmd.verbose:
                print("display: %s" % message, file=sys.stderr)
                sys.stderr.flush()

            monitor.set_message(message)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError, TypeError) as ex:
        print("display: %s" % ex, file=sys.stderr)

    finally:
        if cmd and cmd.verbose:
            print("display: finishing", file=sys.stderr)

        if monitor:
            monitor.stop()
