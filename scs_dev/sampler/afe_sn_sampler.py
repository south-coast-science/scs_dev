"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class AFESNSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, afe, sn):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__afe = afe
        self.__sn = sn


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'afe', self.__afe.sample_station(self.__sn)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AFESNSampler:{runner:%s, afe:%s, sn:%d}" %  (self.runner, self.__afe, self.__sn)


