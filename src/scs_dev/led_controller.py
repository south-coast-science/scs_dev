#!/usr/bin/env python3

"""
Created on 30 Apr 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The led_controller utility operates the two-colour (red / green) LED mounted on the South Coast Science free-to-air
SHT board. LEDs can be made to flash or have steady state. The utility is intended to run as a systemd service, or as
an (un-managed) background process.

The led_controller waits for data on stdin or the named Unix domain socket, then updates the state of the LEDs
accordingly. Updates are in the form of a JSON array containing two single-character strings - the first represents
70% of the duty cycle, the second 30%. If a steady state is required, the two values should be the same.

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
scs_dev/interface_power
scs_dev/led

RESOURCES
https://unix.stackexchange.com/questions/139490/continuous-reading-from-named-pipe-cat-or-tail-f
"""

import json

from scs_core.comms.uds_reader import UDSReader

from scs_core.led.led_state import LEDState

from scs_core.sys.logging import Logging
from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_led_controller import CmdLEDController

from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.led.led_controller import LEDController

from scs_host.bus.i2c import I2C
from scs_host.comms.domain_socket import DomainSocket
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    controller = None
    reader = None
    prev_state = None

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdLEDController()

    # logging...
    Logging.config('led_controller', verbose=cmd.verbose)
    logger = Logging.getLogger()

    logger.info(cmd)

    try:
        I2C.Utilities.open()

        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # UDSReader...
        reader = UDSReader(DomainSocket, cmd.uds)
        logger.info(reader)

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            logger.error("InterfaceConf not available.")
            exit(1)

        interface = interface_conf.interface()

        if interface is None:
            logger.error("interface not available.")
            exit(1)

        # LEDController..
        controller = LEDController(interface.led())
        logger.info(controller)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct()

        controller.start()

        reader.connect()

        for message in reader.messages():
            try:
                jdict = json.loads(message)
            except ValueError:
                continue

            state = LEDState.construct_from_jdict(jdict)

            if state is None or state == prev_state:
                continue

            logger.info(state)

            if not state.is_valid():
                continue

            controller.set_state(state)

            prev_state = state


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        logger.error(repr(ex))

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        logger.info("finishing")

        if reader:
            reader.close()

        if controller:
            controller.stop()

        I2C.Utilities.close()
