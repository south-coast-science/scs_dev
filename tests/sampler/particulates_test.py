#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.data.json import JSONify
from scs_core.sync.timed_runner import TimedRunner
from scs_core.sys.system_id import SystemID

from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_dfe.interface.interface_conf import InterfaceConf
from scs_dfe.particulate.opc_conf import OPCConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

sampler = None

try:
    I2C.open(Host.I2C_SENSORS)

    # SystemID...
    system_id = SystemID.load(Host)
    tag = None if system_id is None else system_id.message_tag()

    # Interface...
    interface_conf = InterfaceConf.load(Host)

    # OPCConf...
    conf = OPCConf('N2', 5, False, None, None)

    # OPCMonitor...
    monitor = conf.opc_monitor(interface_conf.interface(), Host)

    runner = TimedRunner(10)

    sampler = ParticulatesSampler(runner, tag, monitor)
    print(sampler)
    print("-")

    sampler.start()

    time.sleep(11)

    datum = sampler.sample()
    print(datum)
    print("-")

    jstr = JSONify.dumps(datum)
    print(jstr)

finally:
    if sampler:
        sampler.stop()

        I2C.close()
