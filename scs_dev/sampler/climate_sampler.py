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

    def __init__(self, device_id, sht, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__device_id = device_id
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        recorded = LocalizedDatetime.now()

        tag = self.__device_id.message_tag()

        sht_sample = self.__sht.sample()

        return ClimateDatum(tag, recorded, sht_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ClimateSampler:{device_id:%s, sht:%s, timer:%s, sample_count:%d}" % \
               (self.__device_id, self.__sht, self.timer, self.sample_count)
