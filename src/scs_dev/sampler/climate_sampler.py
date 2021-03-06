"""
Created on 18 Feb 2017

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.datetime import LocalizedDatetime

from scs_core.sample.climate_sample import ClimateSample

from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class ClimateSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, sht, barometer=None, altitude=None):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__sht = sht

        self.__barometer = barometer
        self.__altitude = altitude


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        Sampler.reset(self)

        self.__sht.reset()


    def sample(self):
        sht_sample = self.__sht.sample()

        # TODO: get the altitude from GPS if necessary

        if self.__barometer:
            barometer_sample = self.__barometer.sample(altitude=self.__altitude, include_temp=False)
        else:
            barometer_sample = None

        recorded = LocalizedDatetime.now().utc()        # after sampling, so that we can monitor resource contention

        return ClimateSample(self.__tag, recorded, sht_sample, barometer_sample)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "ClimateSampler:{runner:%s, tag:%s, sht:%s, barometer:%s, altitude:%s}" % \
               (self.runner, self.__tag, self.__sht, self.__barometer, self.__altitude)
