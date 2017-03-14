#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.json import JSONify
from scs_core.sys.device_id import DeviceID

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.afe_baseline import AFEBaseline
from scs_dfe.gas.afe_calib import AFECalib
from scs_dfe.gas.pt1000_calib import Pt1000Calib

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

device_id = DeviceID.load_from_host(Host)

if device_id is None:
    print("DeviceID not available.", file=sys.stderr)
    exit()

sht_conf = SHTConf.load_from_host(Host)
sht = sht_conf.int_sht()

calib = Pt1000Calib.load_from_host(Host)
pt1000 = calib.pt1000()

afe_baseline = AFEBaseline.load_from_host(Host)

calib = AFECalib.load_from_host(Host)
sensors = calib.sensors(afe_baseline)


try:
    I2C.open(Host.I2C_SENSORS)

    sampler = GasesSampler(device_id, sht, pt1000, sensors, 1)
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
