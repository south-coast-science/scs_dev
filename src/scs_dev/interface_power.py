#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The interface_power utility is used to simultaneously switch on and off the power to the following peripherals:

* GPS
* OPC
* NDIR
* modem (currently 2G or OPCube only)
* integrated gas sensor interface (digital side only)

Note that not all interface board types are able to switch off all of these subsystems. Where switching is not possible,
no operation is performed, and no exception is raised.

LED control is direct - it bypasses the led_controller process, if running. This enables LED control in service stop
situations, where led_controller service may already have stopped.

The utility supports switch of any combination of peripherals, or all peripherals. Note that, in the case of 'all' the
modem is switched on if the parameter is 1 but is skipped if the parameter is 0.

SYNOPSIS
interface_power.py { [-g ENABLE] [-p ENABLE] [-m ENABLE] [-n ENABLE] [-o ENABLE] [-l { R | A | G | 0 }] | ENABLE_ALL } \
[-v]

EXAMPLES
./interface_power.py 0

RESOURCES
https://github.com/south-coast-science/docs/wiki/Praxis-LED-colours
"""

import sys

from scs_core.sys.signalled_exit import SignalledExit

from scs_dev.cmd.cmd_power import CmdPower

from scs_dfe.gps.gps_conf import GPSConf
from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

try:
    from scs_ndir.gas.ndir.ndir_conf import NDIRConf
except ImportError:
    from scs_core.gas.ndir.ndir_conf import NDIRConf


# --------------------------------------------------------------------------------------------------------------------

def power_gps(enable):
    if gps is None:
        interface.power_gps(enable)             # use interface if no GPS
        return

    if enable:
        gps.power_on()
    else:
        gps.power_off()


def power_ndir(enable):
    if ndir is None:
        interface.power_ndir(enable)             # use interface if no NDIR
        return

    if enable:
        ndir.power_on()
    else:
        ndir.power_off()


def power_opc(enable):
    if opc is None:
        interface.power_opc(enable)             # use interface if no OPC
        return

    if enable:
        opc.power_on()
        opc.operations_on()
    else:
        opc.operations_off()
        opc.power_off()


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    I2C.Utilities.open()

    # ----------------------------------------------------------------------------------------------------------------
    # cmd...

    cmd = CmdPower()

    if not cmd.is_valid():
        cmd.print_help(sys.stderr)
        exit(2)

    if cmd.verbose:
        print("interface_power: %s" % cmd, file=sys.stderr)

    try:
        # ------------------------------------------------------------------------------------------------------------
        # resources...

        # Interface...
        interface_conf = InterfaceConf.load(Host)

        if interface_conf is None:
            print("interface_power: InterfaceConf not available.", file=sys.stderr)
            exit(1)

        interface = interface_conf.interface()

        if cmd.verbose:
            print("interface_power: %s" % interface, file=sys.stderr)
            sys.stderr.flush()

        # GPS...
        gps_conf = GPSConf.load(Host)
        gps = None if gps_conf is None else gps_conf.gps(interface, Host)

        if cmd.verbose and gps:
            print("interface_power: %s" % gps, file=sys.stderr)

        # NDIR...
        ndir_conf = NDIRConf.load(Host)
        ndir = None if ndir_conf is None else ndir_conf.ndir(interface, Host)

        if cmd.verbose and ndir:
            print("interface_power: %s" % ndir, file=sys.stderr)

        # OPC...
        opc_conf = OPCConf.load(Host)
        opc = None if opc_conf is None else opc_conf.opc(interface, Host)

        if cmd.verbose and opc:
            print("interface_power: %s" % opc, file=sys.stderr)

        # LED...
        led = interface.led()

        if cmd.verbose and led:
            print("interface_power: %s" % led, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        # signal handler...
        SignalledExit.construct("interface_power", cmd.verbose)

        if cmd.all is not None:
            interface.power_gases(cmd.all)

            if cmd.all:
                interface.power_modem(cmd.all)          # 'all' shall not switch modem off

            power_gps(cmd.all)
            power_ndir(cmd.all)
            power_opc(cmd.all)

        if cmd.gases is not None:
            interface.power_gases(cmd.gases)

        if cmd.gps is not None:
            power_gps(cmd.gps)

        if cmd.modem is not None:
            interface.power_modem(cmd.modem)

        if cmd.ndir is not None:
            power_ndir(cmd.ndir)

        if cmd.opc is not None:
            power_opc(cmd.opc)

        if cmd.led is not None:
            if led:
                led.colour = cmd.led


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except ConnectionError as ex:
        print("interface_power: %s" % ex, file=sys.stderr)

    except (KeyboardInterrupt, SystemExit):
        pass

    finally:
        if cmd and cmd.verbose:
            print("interface_power: finishing", file=sys.stderr)

        I2C.Utilities.close()
