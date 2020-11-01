#!/usr/bin/env python3

"""
Created on 31 Oct 2020

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.datetime import LocalizedDatetime

from scs_core.gas.afe_calib import AFECalib

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

calib = AFECalib.load(Host)
print(calib)
print("-")

calibrated_on = calib.calibrated_on
print("calibrated_on: %s" % calibrated_on)

calibration_currency = calib.currency()
print("calibration_currency: %s" % calibration_currency)
print("-")

now = LocalizedDatetime.construct_from_iso8601('2016-11-01T12:00:00Z')
print("now: %s" % now)

calibration_currency = calib.currency_at(now)
print("calibration_currency: %s" % calibration_currency)
print("-")
