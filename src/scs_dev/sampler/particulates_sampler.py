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

    def __init__(self, runner, system_id, monitor):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__system_id = system_id
        self.__monitor = monitor


    # ----------------------------------------------------------------------------------------------------------------

    def start(self):
        self.__monitor.on()
        self.__monitor.start()

        # wait for data...
        while self.sample() is None:
            time.sleep(1)


    def stop(self):
        self.__monitor.stop()
        self.__monitor.off()


    def sample(self):
        tag = self.__system_id.message_tag()
        opc_sample = self.__monitor.sample()

        if opc_sample is None:
            return None

        return ParticulatesSample(tag, opc_sample.rec, opc_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{runner:%s, system_id:%s, monitor:%s}" % \
               (self.runner, self.__system_id, self.__monitor)
