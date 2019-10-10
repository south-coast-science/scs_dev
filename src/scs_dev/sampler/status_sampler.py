"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import subprocess

from scs_core.data.localized_datetime import LocalizedDatetime

from scs_core.location.timezone_conf import TimezoneConf

from scs_core.sample.status_sample import StatusSample

from scs_core.sampler.sampler import Sampler

from scs_core.sync.schedule import Schedule

from scs_core.sys.system_temp import SystemTemp
from scs_core.sys.uptime_datum import UptimeDatum

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class StatusSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, airnow, interface, gps_monitor, psu_monitor):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__airnow = airnow

        self.__interface = interface
        self.__gps_monitor = gps_monitor
        self.__psu_monitor = psu_monitor


    # ----------------------------------------------------------------------------------------------------------------

    def start(self):
        try:
            # start...
            if self.__psu_monitor:
                self.__psu_monitor.start()

            if self.__gps_monitor:
                self.__gps_monitor.start()

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass


    def stop(self):
        try:
            if self.__psu_monitor:
                self.__psu_monitor.stop()

            if self.__gps_monitor:
                self.__gps_monitor.stop()

        except (BrokenPipeError, KeyboardInterrupt, SystemExit):
            pass


    def sample(self):
        # timezone...
        timezone_conf = TimezoneConf.load(Host)
        timezone = timezone_conf.timezone()

        # position...
        position = None if self.__gps_monitor is None else self.__gps_monitor.sample()

        # temperature...
        try:
            interface_temp = None if self.__interface is None else self.__interface.temp()
        except OSError:
            interface_temp = self.__interface.null_datum()

        mcu_temp = Host.mcu_temp()

        temperature = SystemTemp.construct(interface_temp, mcu_temp)

        # schedule...
        schedule = Schedule.load(Host)

        # uptime...
        raw = subprocess.check_output('uptime')
        report = raw.decode()

        uptime = UptimeDatum.construct_from_report(None, report)

        # psu_monitor...
        psu_monitor_status = None if self.__psu_monitor is None else self.__psu_monitor.sample()

        # datum...
        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return StatusSample(self.__tag, self.__airnow, recorded, timezone, position, temperature,
                            schedule, uptime, psu_monitor_status)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StatusSampler:{runner:%s, tag:%s, airnow:%s, interface:%s, gps_monitor:%s, psu_monitor:%s}" % \
               (self.runner, self.__tag, self.__airnow, self.__interface, self.__gps_monitor, self.__psu_monitor)
