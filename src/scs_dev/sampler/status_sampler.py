"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

import sys

from scs_core.data.datetime import LocalizedDatetime
from scs_core.location.timezone_conf import TimezoneConf
from scs_core.sample.status_sample import StatusSample
from scs_core.sampler.sampler import Sampler
from scs_core.sync.schedule import Schedule
from scs_core.sys.system_temp import SystemTemp

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class StatusSampler(Sampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, runner, tag, airnow, interface, gps_monitor, psu_conf):
        """
        Constructor
        """
        Sampler.__init__(self, runner)

        self.__tag = tag
        self.__airnow = airnow

        self.__interface = interface
        self.__gps_monitor = gps_monitor
        self.__psu_conf = psu_conf


    # ----------------------------------------------------------------------------------------------------------------

    def start(self):
        try:
            if self.__gps_monitor:
                self.__gps_monitor.start()

        except (ConnectionError, KeyboardInterrupt, SystemExit):
            pass


    def stop(self):
        try:
            if self.__gps_monitor:
                self.__gps_monitor.stop()

        except (ConnectionError, KeyboardInterrupt, SystemExit):
            pass


    # ----------------------------------------------------------------------------------------------------------------

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
            # noinspection PyUnresolvedReferences
            interface_temp = self.__interface.null_datum()

        mcu_temp = Host.mcu_temp()

        temperature = SystemTemp.construct(interface_temp, mcu_temp)

        # schedule...
        schedule = Schedule.load(Host)

        # uptime...
        uptime = Host.uptime()

        # PSUReport...
        psu_report_class = self.__psu_conf.psu_report_class()
        psu_report = None if psu_report_class is None else psu_report_class.load(self.__psu_conf.report_file)

        print("*** StatusSampler.sample - psu_report: %s" % psu_report, file=sys.stderr)
        print("*** StatusSampler.sample - psu_report: %s" % psu_report.as_json(), file=sys.stderr)
        sys.stderr.flush()

        # datum...
        recorded = LocalizedDatetime.now().utc()        # after sampling, so that we can monitor resource contention

        return StatusSample(self.__tag, recorded, self.__airnow, timezone, position, temperature,
                            schedule, uptime, psu_report)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StatusSampler:{runner:%s, tag:%s, airnow:%s, interface:%s, gps_monitor:%s, psu_conf:%s}" % \
               (self.runner, self.__tag, self.__airnow, self.__interface, self.__gps_monitor, self.__psu_conf)
