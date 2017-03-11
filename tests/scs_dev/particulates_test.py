#!/usr/bin/env python3

"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.data.json import JSONify

from scs_dev.sampler.particulates_sampler import ParticulatesSampler


# --------------------------------------------------------------------------------------------------------------------

sampler = None

try:
    tag = "scs-ap1-0"

    sampler = ParticulatesSampler(tag, 10)
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
