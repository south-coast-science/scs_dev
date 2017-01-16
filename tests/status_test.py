#!/usr/bin/env python3

'''
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

from scs_dev.sampler.status_sampler import StatusSampler
from scs_dfe.bus.i2c import I2C
from scs_host.sys.host import Host
from scs_core.common.json import JSONify


# --------------------------------------------------------------------------------------------------------------------

try:
    I2C.open(Host.I2C_SENSORS)

    sampler = StatusSampler(1.0)
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
