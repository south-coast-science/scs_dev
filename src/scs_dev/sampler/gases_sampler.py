"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import time

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sample.gases_sample import GasesSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, ndir_monitor, sht, gas_sensors):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__ndir_monitor = ndir_monitor
        self.__sht = sht
        self.__gas_sensors = gas_sensors


    # ----------------------------------------------------------------------------------------------------------------

    def start(self):
        try:
            if self.__ndir_monitor is None:
                return

            self.__ndir_monitor.start()

            # wait for data...
            while self.__ndir_monitor.sample() is None:
                time.sleep(1.0)

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass


    def stop(self):
        try:
            if self.__ndir_monitor is None:
                return

            self.__ndir_monitor.stop()

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass



    def reset(self):
        Sampler.reset(self)

        self.__sht.reset()


    def sample(self):
        try:
            ndir_datum = None if self.__ndir_monitor is None else self.__ndir_monitor.sample()
        except OSError:
            ndir_datum = self.__ndir_monitor.null_datum()

        try:
            sht_datum = None if self.__sht is None else self.__sht.sample()
        except OSError:
            sht_datum = self.__sht.null_datum()

        try:
            electrochem_datum = None if self.__gas_sensors is None else self.__gas_sensors.sample(sht_datum)
        except OSError:
            electrochem_datum = self.__gas_sensors.null_datum()

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return GasesSample(self.__tag, recorded, ndir_datum, electrochem_datum, sht_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{runner:%s, tag:%s, ndir_monitor:%s, sht:%s}" % \
                    (self.runner, self.__tag, self.__ndir_monitor, self.__sht)
