"""
Created on 20 Oct 2016

@author: Bruno Beloff (bruno.beloff@southcoastscience.com)
"""

from scs_core.data.localized_datetime import LocalizedDatetime
from scs_core.location.gpgga import GPGGA
from scs_core.location.gps_location import GPSLocation
from scs_core.sample.status_datum import StatusDatum
from scs_core.sync.timed_sampler import TimedSampler
from scs_core.sys.system_temp import SystemTemp

from scs_dfe.board.mcp9808 import MCP9808
from scs_dfe.gps.pam7q import PAM7Q

from scs_host.sys.host import Host


# --------------------------------------------------------------------------------------------------------------------

class StatusSampler(TimedSampler):
    """
    classdocs
    """

    # ----------------------------------------------------------------------------------------------------------------

    def __init__(self, system_id, interval, sample_count=None):
        """
        Constructor
        """
        TimedSampler.__init__(self, interval, sample_count)

        self.__system_id = system_id
        self.__board = MCP9808(True)
        self.__gps = PAM7Q()


    # ----------------------------------------------------------------------------------------------------------------

    def reset(self):
        pass


    def sample(self):
        tag = self.__system_id.message_tag()

        # location...
        location = None

        try:
            self.__gps.open()
            gga = self.__gps.report(GPGGA)
            location = GPSLocation.construct(gga)
        except RuntimeError:
            pass

        finally:
            try:
                self.__gps.close()
            except RuntimeError:
                pass

        # temperature...
        try:
            board_sample = self.__board.sample()
        except OSError:
            board_sample = self.__board.null_datum()

        mcu_sample = Host.mcu_temp()

        temperature = SystemTemp.construct(board_sample, mcu_sample)

        # exception...
        exception = None    # TODO: handle exception sending

        recorded = LocalizedDatetime.now()      # after sampling, so that we can monitor resource contention

        return StatusDatum(tag, recorded, location, temperature, exception)


    # ----------------------------------------------------------------------------------------------------------------

    def __str__(self, *args, **kwargs):
        return "StatusSampler:{system_id:%s, board:%s, timer:%s, sample_count:%s}" % \
                    (self.__system_id, self.__board, self.timer, self.sample_count)
