"""
Created on 21 Jun 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.sample.pressure_sample import PressureSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class PressureSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, mpl115a2, altitude):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__mpl115a2 = mpl115a2
        self.__altitude = altitude


    # ----------------------------------------------------------------------------------------------------------------

    def init(self):
        self.__mpl115a2.init()


    def sample(self):
        # TODO: get the altitude from GPS if necessary

        mpl115a2_datum = self.__mpl115a2.sample(self.__altitude)

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return PressureSample(self.__tag, recorded, mpl115a2_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "PressureSampler:{runner:%s, tag:%s, mpl115a2:%s, altitude:%s}" % \
               (self.runner, self.__tag, self.__mpl115a2, self.__altitude)
