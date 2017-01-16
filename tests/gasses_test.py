#!/usr/bin/env python3

'''
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
'''

from scs_core.data.json import JSONify

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.bus.i2c import I2C
from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.afe_conf import AFEConf
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

sht_conf = SHTConf.load(Host)
sht = sht_conf.ext_sht()                # TODO: this should be int_sht() but we don't have one yet

calib = Pt1000Calib.load(Host)
pt1000 = calib.pt1000()

conf = AFEConf.load(Host)
sensors = conf.sensors()

try:
    I2C.open(Host.I2C_SENSORS)

    sampler = GasesSampler(sht, pt1000, sensors, 1)
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
