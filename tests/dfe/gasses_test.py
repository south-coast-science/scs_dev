#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.climate.pressure_conf import PressureConf

from scs_core.data.json import JSONify
from scs_core.sync.timed_runner import TimedRunner
from scs_core.sys.system_id import SystemID

from scs_dev.sampler.gases_sampler import GasesSampler

from scs_dfe.climate.sht_conf import SHTConf
from scs_dfe.gas.scd30.scd30_conf import SCD30Conf
from scs_dfe.interface.interface_conf import InterfaceConf

from scs_host.bus.i2c import I2C
from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

interface = None

try:
    I2C.Sensors.open()

    # ----------------------------------------------------------------------------------------------------------------
    # resources...

    # SystemID...
    system_id = SystemID.load(Host)
    tag = None if system_id is None else system_id.message_tag()

    # MPL115A2...
    pressure_conf = PressureConf.load(Host)
    barometer = None if pressure_conf is None else pressure_conf.sensor(None)

    # NDIR...
    scd30_conf = SCD30Conf.load(Host)
    scd30 = None if scd30_conf is None else scd30_conf.scd30()

    # SHT...
    sht_conf = SHTConf.load(Host)
    sht = sht_conf.int_sht()

    # AFE...
    interface_conf = InterfaceConf.load(Host)
    interface = interface_conf.interface()

    gas_sensors = interface.gas_sensors(Host)

    # runner...
    runner = TimedRunner(0)

    sampler = GasesSampler(runner, tag, barometer, scd30, sht, gas_sensors)
    print(sampler)
    print("-")

    # ----------------------------------------------------------------------------------------------------------------
    # run...

    interface.power_gases(True)

    sampler.init(scd30_conf)

    while True:
        time.sleep(6)

        datum = sampler.sample()
        print(datum)
        print("-")

        jstr = JSONify.dumps(datum)
        print(jstr)
        print("=")

finally:
    if interface:
        interface.power_gases(False)

    I2C.Sensors.close()
