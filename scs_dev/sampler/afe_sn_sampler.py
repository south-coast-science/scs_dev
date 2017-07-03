"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sampler.sampler import Sampler

from scs_dfe.gas.afe import AFE


# --------------------------------------------------------------------------------------------------------------------

class AFESNSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, pt1000_conf, pt1000, sensors, sn):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__sn = sn
        self.__afe = AFE(pt1000_conf, pt1000, sensors)


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'afe', self.__afe.sample_station(self.__sn)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AFESNSampler:{runner:%s, afe:%s, sn:%d}" %  (self.runner, self.__afe, self.__sn)


