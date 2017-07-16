"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class AFESampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, afe):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__afe = afe


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'afe', self.__afe.sample()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "AFESampler:{runner:%s, afe:%s}" % (self.runner, self.__afe)


