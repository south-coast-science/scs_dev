"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.sample.gases_datum import GasesDatum
from scs_core.sync.sampler import Sampler

from scs_dfe.gas.afe import AFE


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, tag, sht, pt1000, sensors, interval, sample_count=0):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__tag = tag
        self.__afe = AFE(pt1000, sensors)
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        recorded = LocalizedDatetime.now()

        sht_datum = self.__sht.sample()
        afe_datum = self.__afe.sample(sht_datum)

        return GasesDatum(self.__tag, recorded, afe_datum, sht_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{tag:%s, afe:%s, sht:%s, timer:%s, sample_count:%d}" % \
                    (self.__tag, self.__afe, self.__sht, self.timer, self.sample_count)
