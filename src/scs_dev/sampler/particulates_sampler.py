"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.sample.particulates_sample import ParticulatesSample

from scs_core.sampler.sampler import Sampler


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

        if opc_sample.is_zero():                        # do not return zero samples
            return None

        return ParticulatesSample(self.__tag, opc_sample.rec, opc_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{runner:%s, tag:%s, opc_monitor:%s}" % \
               (self.runner, self.__tag, self.__opc_monitor)
