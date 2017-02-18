"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.climate_datum import ClimateDatum
from scs_core.sync.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class ClimateSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, sht, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        recorded = LocalizedDatetime.now()

        sht_sample = self.__sht.sample()

        return ClimateDatum(recorded, sht_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ClimateSampler:{sht:%s, timer:%s, sample_count:%d}" % (self.__sht, self.timer, self.sample_count)
