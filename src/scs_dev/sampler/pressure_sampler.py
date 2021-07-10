"""
Created on 21 Jun 2018

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.datetime import LocalizedDatetime

from scs_core.sample.pressure_sample import PressureSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class PressureSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, barometer, altitude):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__barometer = barometer
        self.__altitude = altitude


    # ----------------------------------------------------------------------------------------------------------------

    def init(self):
        self.__barometer.init()


    def sample(self):
        barometer_sample = self.__barometer.sample(altitude=self.__altitude)
        rec = LocalizedDatetime.now().utc()         # after sampling, so that we can monitor resource contention

        return PressureSample(self.__tag, rec, barometer_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "PressureSampler:{runner:%s, tag:%s, barometer:%s, altitude:%s}" % \
               (self.runner, self.__tag, self.__barometer, self.__altitude)
