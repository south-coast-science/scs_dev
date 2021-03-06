"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.datetime import LocalizedDatetime
from scs_core.sample.gases_sample import GasesSample
from scs_core.sampler.sampler import Sampler


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, mpl115a2, scd30, sht, sensor_interface):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag

        self.__mpl115a2 = mpl115a2                              # MPL115A2
        self.__scd30 = scd30                                    # SCD30
        self.__sht = sht                                        # SHT31
        self.__sensor_interface = sensor_interface              # SensorInterface


    # ----------------------------------------------------------------------------------------------------------------

    def init(self, scd30_conf):
        if self.__mpl115a2:
            self.__mpl115a2.init()
            mpl115a2_datum = self.__mpl115a2.sample()

        else:
            mpl115a2_datum = None

        if not self.__scd30:
            return

        actual_press = None if mpl115a2_datum is None else mpl115a2_datum.actual_press

        self.__scd30.set_auto_self_calib(True)
        self.__scd30.set_measurement_interval(scd30_conf.sample_interval)

        self.__scd30.stop_periodic_measurement()
        self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)

        self.__scd30.sample()
        self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)


    def sample(self):
        try:
            mpl115a2_datum = None if self.__mpl115a2 is None else self.__mpl115a2.sample()
        except OSError:
            # noinspection PyUnresolvedReferences
            mpl115a2_datum = self.__mpl115a2.null_datum()

        actual_press = None if mpl115a2_datum is None else mpl115a2_datum.actual_press

        try:
            if self.__scd30:
                if self.__mpl115a2 and actual_press is None:
                    scd30_datum = self.__scd30.null_datum()

                    print("gases_sampler: pA specified but unavailable", file=sys.stderr)
                    sys.stderr.flush()

                else:
                    scd30_datum = self.__scd30.sample()

                self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)

            else:
                scd30_datum = None

        except OSError:
            # noinspection PyUnresolvedReferences
            scd30_datum = self.__scd30.null_datum()

        try:
            sht_datum = None if self.__sht is None else self.__sht.sample()
        except OSError:
            # noinspection PyUnresolvedReferences
            sht_datum = self.__sht.null_datum()

        try:
            electrochem_datum = None if self.__sensor_interface is None else self.__sensor_interface.sample(sht_datum)
        except OSError:
            # noinspection PyUnresolvedReferences
            electrochem_datum = self.__sensor_interface.null_datum()

        recorded = LocalizedDatetime.now().utc()        # after sampling, so that we can monitor resource contention

        return GasesSample(self.__tag, recorded, scd30_datum, electrochem_datum, sht_datum)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{runner:%s, tag:%s, mpl115a2:%s, scd30:%s, sht:%s}" % \
                    (self.runner, self.__tag, self.__mpl115a2, self.__scd30, self.__sht)
