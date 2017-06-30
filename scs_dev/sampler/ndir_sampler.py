"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class NDIRSampler(Sampler):
    """
    classdocs
    """
    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyShadowingNames
    def __init__(self, runner, ndir):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__ndir = ndir


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return 'ndir', self.__ndir.sample()


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "NDIRSampler:{runner:%s, ndir:%s}" %  (self.runner , self.__ndir)


