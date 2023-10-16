#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.json import JSONify
from scs_core.sync.timed_runner import TimedRunner
from scs_core.sys.system_id import SystemID

from scs_dev.sampler.status_sampler import StatusSampler

from scs_dfe.gps.gps_conf import GPSConf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host

try:
    from scs_psu.psu.psu_conf import PSUConf
except ImportError:
    from scs_core.psu.psu_conf import PSUConf


# --------------------------------------------------------------------------------------------------------------------

try:
    I2C.Sensors.open()

    system_id = SystemID.load(Host)
    tag = None if system_id is None else system_id.message_tag()

    # Interface...
    interface_conf = InterfaceConf.load(Host)

    # GPS...
    gps_conf = GPSConf.load(Host)
    gps_monitor = gps_conf.gps_monitor(interface_conf.interface(), Host)

    # PSU...
    psu_conf = PSUConf.load(Host)

    runner = TimedRunner(10)

    sampler = StatusSampler(runner, tag, Host, None, None, gps_monitor, psu_conf)
    print(sampler)
    print("-")

    sampler.reset()

    datum = sampler.sample()
    print(datum)
    print("-")

    jstr = JSONify.dumps(datum)
    print(jstr)

finally:
    I2C.Sensors.close()
