#!/usr/bin/env python3

"""
Created on 28 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

DESCRIPTION
The interface_power utility is used to simultaneously switch on and off the power to the following peripherals:

* GPS
* OPC
* NDIR
* modem (currently 2G only)
* integrated gas sensor interface (digital side only)

Note that not all interface board types are able to switch off all of these subsystems. Where switching is not possible,
no operation is performed, and no exception is raised.

The utility supports switch of any combination of peripherals, or all peripherals. Note that, in the case of 'all' the
modem is not included.

SYNOPSIS
interface_power.py { [-g ENABLE] [-p ENABLE] [-m ENABLE] [-n ENABLE] [-o ENABLE] | ENABLE_ALL } [-v]

EXAMPLES
./interface_power.py 0
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
    from scs_ndir.gas.ndir_conf import NDIRConf
except ImportError:
    from scs_core.gas.ndir_conf import NDIRConf


# --------------------------------------------------------------------------------------------------------------------

def power_gps(enable):
    if gps is None:
        return

    if enable:
        gps.power_on()
    else:
        gps.power_off()


def power_ndir(enable):
    if ndir is None:
        return

    if enable:
        ndir.power_on()
    else:
        ndir.power_off()


def power_opc(enable):
    if opc is None:
        return

    if enable:
        opc.power_on()
        opc.operations_on()
    else:
        # opc.operations_off()
        opc.power_off()


# --------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':

    I2C.open(Host.I2C_SENSORS)

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

        # signal handler...
        SignalledExit.construct("interface_power", cmd.verbose)

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

        if cmd.verbose and gps_conf:
            print("interface_power: %s" % gps_conf, file=sys.stderr)

        # OPC...
        opc_conf = OPCConf.load(Host)
        opc = None if opc_conf is None else opc_conf.opc(interface, Host)

        if cmd.verbose and opc_conf:
            print("interface_power: %s" % opc_conf, file=sys.stderr)

        # NDIR...
        ndir_conf = NDIRConf.load(Host)
        ndir = None if ndir_conf is None else ndir_conf.ndir(interface, Host)

        if cmd.verbose and ndir_conf:
            print("interface_power: %s" % ndir_conf, file=sys.stderr)


        # ------------------------------------------------------------------------------------------------------------
        # run...

        if cmd.all is not None:
            interface.power_gases(cmd.all)
            power_gps(cmd.all)
            power_ndir(cmd.all)
            power_opc(cmd.all)

            # io.led_red = True             # TODO: fix LED control

        if cmd.gases is not None:
            interface.power_gases(cmd.gases)

        if cmd.gps is not None:
            power_gps(cmd.gps)

        if cmd.modem is not None:
            pass                            # TODO: implement 2G modem power control

        if cmd.ndir is not None:
            power_ndir(cmd.ndir)

        if cmd.opc is not None:
            power_opc(cmd.opc)


    # ----------------------------------------------------------------------------------------------------------------
    # end...

    except (BrokenPipeError, ConnectionResetError, TypeError) as ex:
        print("interface_power: %s" % ex, file=sys.stderr)

    finally:
        if cmd and cmd.verbose:
            print("interface_power: finishing", file=sys.stderr)

        I2C.close()
