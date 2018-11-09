"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.sample.particulates_sample import ParticulatesSample

from scs_core.sampler.sampler import Sampler


# TODO: handle the case of duff OPC on BeagleBone - don't report these...
# val.mtf1,val.bins.11,val.bins.12,val.bins.13,val.bins.14,val.bins.15,val.bins.0,val.bins.1,val.bins.2,val.bins.3,
# val.bins.4,val.bins.5,val.bins.6,val.bins.7,val.bins.8,val.bins.9,val.bins.10,val.pm1,val.mtf5,val.pm2p5,val.mtf3,
# val.pm10,val.mtf7,val.per,rec,tag
# 255.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,65535.0,
# 65535.0,65535.0,,255.0,,255.0,,255.0,,2018-09-01T09:25:04.270+00:00,scs-bgb-413

# --------------------------------------------------------------------------------------------------------------------

class ParticulatesSampler(Sampler):
    """
    classdocs
    """

    SCHEDULE_SEMAPHORE =    "scs-particulates"        # hard-coded path

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, opc_monitor):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__opc_monitor = opc_monitor


    # ----------------------------------------------------------------------------------------------------------------

    def start(self):
        self.__opc_monitor.start()

        # wait for data...
        while self.__opc_monitor.sample() is None:
            time.sleep(1.0)


    def stop(self):
        self.__opc_monitor.stop()


    def sample(self):
        opc_sample = self.__opc_monitor.sample()

        if opc_sample is None or opc_sample.is_zero():      # do not return zero samples
            return None

        return ParticulatesSample(self.__tag, opc_sample.rec, opc_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{runner:%s, tag:%s, opc_monitor:%s}" % \
               (self.runner, self.__tag, self.__opc_monitor)
