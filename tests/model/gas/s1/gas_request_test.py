#!/usr/bin/env python3

"""
Created on 11 Nov 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.json import JSONify
from scs_core.data.str import Str

from scs_core.model.gas.s1.gas_request import GasRequest

from scs_core.gas.afe_calib import AFECalib

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

t_slope = 0.0
rh_slope = 0.1

try:
    I2C.open(Host.I2C_SENSORS)

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    sht_conf = SHTConf.load(Host)
    sht = sht_conf.ext_sht()
    print(sht)

    calib = AFECalib.load(Host)
    print(calib)

    interface_conf = InterfaceConf.load(Host)
    interface = interface_conf.interface()
    print(interface)

    sensor_interface = interface.gas_sensors(Host)
    print(sensor_interface)
    print("-")

    sensor_calibs = calib.sensor_calibs()
    print(Str.collection(sensor_calibs))
    print("-")

    sampler = GasesSampler(None, 'test', None, None, sht, sensor_interface)
    print(sampler)
    print("=")


    # ----------------------------------------------------------------------------------------------------------------
    # run...

    calib_age = calib.age()

    sample = sampler.sample()
    print(sample)
    print("-")

    print(JSONify.dumps(sample))
    print("-")

    request = GasRequest(sample, t_slope, rh_slope, sensor_calibs, calib_age)
    print(request)
    print("-")

    print(JSONify.dumps(request.as_json()))

finally:
    I2C.close()
