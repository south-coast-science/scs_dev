"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.climate_datum import ClimateDatum
from scs_core.sync.timed_sampler import TimedSampler


# --------------------------------------------------------------------------------------------------------------------

class ClimateSampler(TimedSampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, system_id, sht, interval, sample_count=None):
        """
        Constructor
        """
        TimedSampler.__init__(self, interval, sample_count)

        self.__system_id = system_id
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        tag = self.__system_id.message_tag()

        sht_sample = self.__sht.sample()

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return ClimateDatum(tag, recorded, sht_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ClimateSampler:{system_id:%s, sht:%s, timer:%s, sample_count:%s}" % \
               (self.__system_id, self.__sht, self.timer, self.sample_count)
