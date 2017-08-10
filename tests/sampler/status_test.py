#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.json import JSONify
from scs_core.sync.timed_runner import TimedRunner
from scs_core.sys.system_id import SystemID

from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.gps.gps_conf import GPSConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

try:
    I2C.open(Host.I2C_SENSORS)

    system_id = SystemID.load_from_host(Host)

    if system_id is None:
        print("SystemID not available.", file=sys.stderr)
        exit()

    # board...
    board = MCP9808(True)

    # GPS...
    gps_conf = GPSConf.load_from_host(Host)
    gps = gps_conf.gps()

    # PSU...
    psu_conf = PSUConf.load_from_host(Host)
    psu = psu_conf.psu(Host)

    runner = TimedRunner(10)

    sampler = StatusSampler(runner, system_id, board, gps, psu)
    print(sampler)
    print("-")

    sampler.reset()

    datum = sampler.sample()
    print(datum)
    print("-")

    jstr = JSONify.dumps(datum)
    print(jstr)

finally:
    I2C.close()
