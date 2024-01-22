"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.datetime import LocalizedDatetime

from scs_core.sample.gases_sample import GasesSample
from scs_core.sampler.sampler import Sampler

from scs_core.sys.logging import Logging


# --------------------------------------------------------------------------------------------------------------------

class GasesSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, barometer, scd30, sht, sensor_interface):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag

        self.__barometer = barometer                                # ICP10101 or MPL115A2
        self.__scd30 = scd30                                        # SCD30
        self.__sht = sht                                            # SHT31
        self.__sensor_interface = sensor_interface                  # GasSensorInterface

        self.__src = None if sensor_interface is None else sensor_interface.src()
        self.__logger = Logging.getLogger()


    # ----------------------------------------------------------------------------------------------------------------

    def init(self, scd30_conf):
        if self.__barometer:
            self.__barometer.init()
            pressure_datum = self.__barometer.sample()

        else:
            pressure_datum = None

        if not self.__scd30:
            return

        actual_press = None if pressure_datum is None else pressure_datum.actual_press

        self.__scd30.set_auto_self_calib(True)
        self.__scd30.set_measurement_interval(scd30_conf.sample_interval)

        self.__scd30.stop_periodic_measurement()
        self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)

        self.__scd30.sample()
        self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)


    def sample(self):
        try:
            pressure_datum = None if self.__barometer is None else self.__barometer.sample()
        except OSError as ex:
            self.__logger("sample error 1: %s" % repr(ex))
            # noinspection PyUnresolvedReferences
            pressure_datum = self.__barometer.null_datum()

        actual_press = None if pressure_datum is None else pressure_datum.actual_press

        try:
            if self.__scd30:
                if self.__barometer and actual_press is None:
                    self.__logger("sample error 2: pA specified but unavailable")
                    scd30_datum = self.__scd30.null_datum()

                else:
                    scd30_datum = self.__scd30.sample()

                self.__scd30.start_periodic_measurement(ambient_pressure_kpa=actual_press)

            else:
                scd30_datum = None

        except OSError as ex:
            self.__logger("sample error 3: %s" % repr(ex))
            scd30_datum = self.__scd30.null_datum()

        try:
            sht_datum = None if self.__sht is None else self.__sht.sample()
        except OSError as ex:
            self.__logger("sample error 4: %s" % repr(ex))
            # noinspection PyUnresolvedReferences
            sht_datum = self.__sht.null_datum()

        try:
            electrochem_datum = None if self.__sensor_interface is None else self.__sensor_interface.sample(sht_datum)
        except OSError as ex:
            self.__logger("sample error 5: %s" % repr(ex))
            # noinspection PyUnresolvedReferences
            electrochem_datum = self.__sensor_interface.null_datum()

        recorded = LocalizedDatetime.now().utc()        # after sampling, so that we can monitor resource contention

        return GasesSample(self.__tag, recorded, scd30_datum, electrochem_datum, sht_datum, src=self.__src)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "GasesSampler:{runner:%s, tag:%s, src:%s, barometer:%s, scd30:%s, sht:%s}" % \
                    (self.runner, self.__tag, self.__src, self.__barometer, self.__scd30, self.__sht)
