"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sample.gases_sample import GasesSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, system_id, ndir, sht, afe):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__system_id = system_id
        self.__ndir = ndir
        self.__sht = sht
        self.__afe = afe


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        Sampler.reset(self)

        self.__sht.reset()


    def sample(self):
        tag = self.__system_id.message_tag()

        try:
            co2_datum = None if self.__ndir is None else self.__ndir.sample_co2(True)
        except OSError:
            co2_datum = self.__ndir.null_datum()

        try:
            sht_datum = None if self.__sht is None else self.__sht.sample()
        except OSError:
            sht_datum = self.__sht.null_datum()

        try:
            afe_datum = None if self.__afe is None else self.__afe.sample(sht_datum)
        except OSError:
            afe_datum = self.__afe.null_datum()

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return GasesSample(tag, recorded, co2_datum, afe_datum, sht_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{runner:%s, system_id:%s, ndir:%s, sht:%s, afe:%s}" % \
                    (self.runner, self.__system_id, self.__ndir, self.__sht, self.__afe)
