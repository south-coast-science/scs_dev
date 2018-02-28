"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sample.climate_sample import ClimateSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class ClimateSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, sht):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        Sampler.reset(self)

        self.__sht.reset()


    def sample(self):
        sht_sample = self.__sht.sample()

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return ClimateSample(self.__tag, recorded, sht_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ClimateSampler:{runner:%s, tag:%s, sht:%s}" % (self.runner, self.__tag, self.__sht)
