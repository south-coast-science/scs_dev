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

    def __init__(self, system_id, sht, pt1000_conf, pt1000, sensors, interval, sample_count=None):
        """
        Constructor
        """
        Sampler.__init__(self, interval, sample_count)

        self.__system_id = system_id
        self.__afe = AFE(pt1000_conf, pt1000, sensors)
        self.__sht = sht


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        self.__sht.reset()


    def sample(self):
        tag = self.__system_id.message_tag()

        sht_datum = self.__sht.sample()
        afe_datum = self.__afe.sample(sht_datum)

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return GasesDatum(tag, recorded, afe_datum, sht_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{system_id:%s, afe:%s, sht:%s, timer:%s, sample_count:%s}" % \
                    (self.__system_id, self.__afe, self.__sht, self.timer, self.sample_count)
