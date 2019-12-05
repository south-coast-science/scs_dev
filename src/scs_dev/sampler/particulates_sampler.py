"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.sampler.sampler import Sampler


# TODO: add sht  - None if use OPC-internal / if no rH source, exg values are None

# --------------------------------------------------------------------------------------------------------------------

class ParticulatesSampler(Sampler):
    """
    classdocs
    """

    SCHEDULE_SEMAPHORE =    "scs-particulates"          # hard-coded path

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
        while True:
            if self.__opc_monitor.sample() is not None:
                break

            time.sleep(1.0)


    def stop(self):
        try:
            self.__opc_monitor.stop()

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass


    def sample(self):
        datum = self.__opc_monitor.sample()

        if datum is None or datum.is_zero():
            return None

        return datum.as_sample(self.__tag)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ParticulatesSampler:{runner:%s, tag:%s, opc_monitor:%s}" % \
               (self.runner, self.__tag, self.__opc_monitor)
