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
https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f"""

import os
import json
import sys

from scs_core.sys.signalled_exit import SignalledExit

from scs_core.data.json import JSONify

from scs_dev.cmd.cmd_led_controller import CmdLEDController

from scs_dfe.display.led_controller import LEDController
from scs_dfe.display.led_state import LEDState

from scs_host.bus.i2c import I2C
from scs_host.comms.domain_socket import DomainSocket
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------
# input reader...

class LEDControllerReader(object):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, uds_name):
        """
        Constructor
        """
        if uds_name is None:
            self.__uds = None
            return

        try:
            os.remove(uds_name)             # override any previous use of the UDS
        except OSError:
            pass

        self.__uds = DomainSocket(uds_name)


    # ----------------------------------------------------------------------------------------------------------------

    def connect(self):
        if self.__uds:
            self.__uds.connect(False)


    def close(self):
        if self.__uds:
            self.__uds.close()


    def messages(self):
        if self.__uds:
            for message in self.__uds.read():
                yield message.strip()

        else:
            for message in sys.stdin:
                yield message.strip()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "LEDControllerReader:{uds:%s}" % self.__uds


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

        # signal handler...
        SignalledExit.construct("led_controller", cmd.verbose)

        # LEDControllerReader...
        reader = LEDControllerReader(cmd.uds)

        if cmd.verbose:
            print("led_controller: %s" % reader, file=sys.stderr)

        # LEDController..
        controller = LEDController()

        if cmd.verbose:
            print("led_controller: %s" % controller, file=sys.stderr)
            sys.stderr.flush()


        # ------------------------------------------------------------------------------------------------------------
        # run...

        reader.connect()

        controller.start()

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

    except (BrokenPipeError, ConnectionResetError):
        pass

    finally:
        if cmd.verbose:
            print("led_controller: finishing", file=sys.stderr)

        if reader:
            reader.close()

        if controller:
            controller.stop()

        I2C.close()
