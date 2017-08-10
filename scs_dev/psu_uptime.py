#!/usr/bin/env python3

"""
Created on 13 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)

command line example:
./ps.py
"""

from scs_core.data.json import JSONify

from scs_host.sys.host import Host

from scs_psu.psu.psu import PSU


# --------------------------------------------------------------------------------------------------------------------

psu = PSU(Host.psu_device())

uptime = psu.uptime()

print(JSONify.dumps(uptime))
