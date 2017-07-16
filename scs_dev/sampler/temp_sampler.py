"""
Created on 30 Jun 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.sampler.sampler import Sampler

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class TempSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    # noinspection PyShadowingNames
    def __init__(self, runner, int_climate, ext_climate, afe, board):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__int_climate = int_climate
        self.__ext_climate = ext_climate
        self.__afe = afe
        self.__board = board

        self.__int_climate.reset()
        self.__ext_climate.reset()


    # ----------------------------------------------------------------------------------------------------------------

    def sample(self):
        return (('int', self.__int_climate.sample()), ('ext', self.__ext_climate.sample()),
                ('pt1', self.__afe.sample_temp()), ('brd', self.__board.sample()), ('host', Host.mcu_temp()))


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "TempSampler:{runner:%s}" % self.runner


