#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.data.json import JSONify
from scs_core.sys.device_id import DeviceID

from scs_dev.sampler.particulates_sampler import ParticulatesSampler

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

sampler = None

try:
    device_id = DeviceID.load_from_host(Host)

    if device_id is None:
        print("DeviceID not available.", file=sys.stderr)
        exit()

    sampler = ParticulatesSampler(device_id, 10)
    print(sampler)
    print("-")

    sampler.on()
    sampler.reset()

    time.sleep(5)

    datum = sampler.sample()
    print(datum)
    print("-")

    jstr = JSONify.dumps(datum)
    print(jstr)

finally:
    if sampler:
        sampler.off()
