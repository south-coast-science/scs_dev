#!/usr/bin/env python3

"""
Created on 30 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The led_controller utility operates the a two-colour (red / green) LED mounted on the South Coast Science free-to-air
SHT board. LEDs can be made to flash or have steady state. The utility is intended to run as a systemd service, or as
an (un-managed) background process.

The led_controller waits for data on stdin or the named Unix domain socket, then updates the state of the LEDs
accordingly. Updates are in the form of a JSON array containing two single-character strings - the first represents
80% of the duty cycle, the second 20%. If a steady state is required, the two values should be the same.

When the led_controller starts, the LEDs remain in their previous state. When the led_controller terminates,
the LEDs remain in their last state.

SYNOPSIS
led_controller -v -u scs_led_control.uds

EXAMPLES
( tail -f ~/SCS/pipes/led_control_pipe & ) | ./led_controller.py -v &
./led_controller.py -v -u /home/scs/SCS/pipes/scs_led_control.uds

DOCUMENT EXAMPLE
{"colour0": "R", "colour1": "G"}

SEE ALSO
scs_dev/led

RESOURCES
https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import json
import sys

from scs_core.sys.signalled_exit import SignalledExit

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_led_controller import CmdLEDController
from scs_dev.handler.uds_reader import UDSReader

from scs_dfe.interface.interface_conf import InterfaceConf

from scs_dfe.led.led_controller import LEDController
from scs_dfe.led.led_state import LEDState

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    controller = None
    reader = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLEDController()

    if cmd.verbose:
        print("led_controller: %s" % cmd, file=sys.stderr)
        sys.stderr.flush()

    try:
        I2C.open(Host.I2C_SENSORS)

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # UDSReader...
        reader = UDSReader(cmd.uds)

        if cmd.verbose:
            print("led_controller: %s" % reader, file=sys.stderr)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("led_controller: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        if interface is None:
            print("led_controller: Interface not available.", file=sys.stderr)
            exit(1)

        # LEDController..
        controller = LEDController(interface.led())

        if cmd.verbose:
            print("led_controller: %s" % controller, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        controller.start()

        # signal handler...
        SignalledExit.construct("led_controller", cmd.verbose)

        reader.connect()

        for line in reader.messages():
            try:
                jdict = json.loads(line)
            except ValueError:
                continue

            state = LEDState.construct_from_jdict(jdict)

            if state is None:
                continue

            if cmd.verbose:
                print("led_controller: %s" % JSONify.dumps(state), file=sys.stderr)
                sys.stderr.flush()

            if not state.is_valid():
                continue

            controller.set_state(state)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError, TypeError) as ex:
        print("led_controller: %s" % ex, file=sys.stderr)

    finally:
        if cmd and cmd.verbose:
            print("led_controller: finishing", file=sys.stderr)

        if reader:
            reader.close()

        if controller:
            controller.stop()

        I2C.close()
